#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from html import unescape
from typing import Callable, Iterable

import requests
from bs4 import BeautifulSoup


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
)


@dataclass
class PaperHit:
    provider: str
    title: str
    url: str
    year: str | None = None
    authors: str | None = None
    venue: str | None = None
    abstract: str | None = None
    doi: str | None = None
    is_preprint: bool = False


def clean_text(value: str | None) -> str | None:
    if not value:
        return None
    value = unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def clip(value: str | None, limit: int = 420) -> str | None:
    if not value:
        return None
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def session_get(url: str, **kwargs) -> requests.Response:
    headers = kwargs.pop("headers", {})
    headers.setdefault("User-Agent", USER_AGENT)
    response = requests.get(url, headers=headers, timeout=30, **kwargs)
    response.raise_for_status()
    return response


def query_pubmed(query: str, limit: int) -> list[PaperHit]:
    search_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
        + urllib.parse.urlencode(
            {"db": "pubmed", "term": query, "retmode": "json", "retmax": limit}
        )
    )
    ids = session_get(search_url).json()["esearchresult"].get("idlist", [])
    if not ids:
        return []

    summary_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"
        + urllib.parse.urlencode(
            {"db": "pubmed", "id": ",".join(ids), "retmode": "json"}
        )
    )
    summary = session_get(summary_url).json()["result"]

    fetch_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
        + urllib.parse.urlencode(
            {"db": "pubmed", "id": ",".join(ids), "retmode": "xml"}
        )
    )
    root = ET.fromstring(session_get(fetch_url).text)
    abstract_map: dict[str, str] = {}
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        pieces = [clean_text(x.text or "") for x in article.findall(".//Abstract/AbstractText")]
        pieces = [x for x in pieces if x]
        if pmid and pieces:
            abstract_map[pmid] = " ".join(pieces)

    hits: list[PaperHit] = []
    for pmid in ids:
        item = summary.get(pmid, {})
        authors = ", ".join(a.get("name", "") for a in item.get("authors", [])[:6]).strip(", ")
        article_ids = item.get("articleids", [])
        doi = next((x.get("value") for x in article_ids if x.get("idtype") == "doi"), None)
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        hits.append(
            PaperHit(
                provider="pubmed",
                title=clean_text(item.get("title")) or f"PubMed {pmid}",
                url=url,
                year=str(item.get("pubdate", ""))[:4] or None,
                authors=authors or None,
                venue=clean_text(item.get("fulljournalname")),
                abstract=clip(abstract_map.get(pmid)),
                doi=doi,
                is_preprint=False,
            )
        )
    return hits


def query_europe_pmc(query: str, limit: int, preprints_only: bool) -> list[PaperHit]:
    filters = [query]
    if preprints_only:
        filters.append('SRC:PPR')
    q = " AND ".join(f"({part})" for part in filters)
    url = (
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
        + urllib.parse.urlencode(
            {
                "query": q,
                "format": "json",
                "resultType": "core",
                "pageSize": limit,
            }
        )
    )
    items = session_get(url).json().get("resultList", {}).get("result", [])
    hits: list[PaperHit] = []
    for item in items:
        source = (item.get("source") or "").upper()
        is_preprint = source == "PPR" or (item.get("pubType") or "").lower() == "preprint"
        url = item.get("doi")
        if url:
            url = f"https://doi.org/{url}"
        else:
            url = item.get("fullTextUrlList", {}).get("fullTextUrl", [{}])[0].get("url")
        if not url and item.get("id"):
            url = f"https://europepmc.org/article/{source.lower()}/{item['id']}"
        hits.append(
            PaperHit(
                provider="europepmc",
                title=clean_text(item.get("title")) or "Untitled Europe PMC hit",
                url=url or "https://europepmc.org/",
                year=str(item.get("pubYear") or "") or None,
                authors=clean_text(item.get("authorString")),
                venue=clean_text(item.get("journalTitle")),
                abstract=clip(clean_text(item.get("abstractText"))),
                doi=item.get("doi"),
                is_preprint=is_preprint,
            )
        )
    return hits


def query_arxiv(query: str, limit: int) -> list[PaperHit]:
    url = (
        "https://export.arxiv.org/api/query?"
        + urllib.parse.urlencode(
            {"search_query": f"all:{query}", "start": 0, "max_results": limit}
        )
    )
    root = ET.fromstring(session_get(url).text)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    hits: list[PaperHit] = []
    for entry in root.findall("a:entry", ns):
        authors = [clean_text(a.findtext("a:name", default="", namespaces=ns)) for a in entry.findall("a:author", ns)]
        authors = [a for a in authors if a]
        hits.append(
            PaperHit(
                provider="arxiv",
                title=clean_text(entry.findtext("a:title", default="", namespaces=ns)) or "Untitled arXiv hit",
                url=clean_text(entry.findtext("a:id", default="", namespaces=ns)) or "https://arxiv.org/",
                year=(entry.findtext("a:published", default="", namespaces=ns) or "")[:4] or None,
                authors=", ".join(authors[:6]) or None,
                venue="arXiv",
                abstract=clip(clean_text(entry.findtext("a:summary", default="", namespaces=ns))),
                is_preprint=True,
            )
        )
    return hits


def parse_scholar_year(block_text: str) -> str | None:
    match = re.search(r"\b(19|20)\d{2}\b", block_text)
    return match.group(0) if match else None


def query_scholar(query: str, limit: int) -> list[PaperHit]:
    url = "https://scholar.google.com/scholar?" + urllib.parse.urlencode({"q": query, "hl": "en"})
    soup = BeautifulSoup(session_get(url).text, "html.parser")
    hits: list[PaperHit] = []
    for card in soup.select("div.gs_r.gs_or.gs_scl")[:limit]:
        title_el = card.select_one("h3.gs_rt")
        if not title_el:
            continue
        link_el = title_el.find("a")
        title = clean_text(title_el.get_text(" ", strip=True))
        meta = clean_text(card.select_one(".gs_a").get_text(" ", strip=True) if card.select_one(".gs_a") else "")
        snippet = clean_text(card.select_one(".gs_rs").get_text(" ", strip=True) if card.select_one(".gs_rs") else "")
        url = link_el["href"] if link_el and link_el.get("href") else "https://scholar.google.com/"
        hits.append(
            PaperHit(
                provider="scholar",
                title=title or "Untitled Scholar hit",
                url=url,
                year=parse_scholar_year(meta or ""),
                authors=meta,
                abstract=clip(snippet),
            )
        )
    return hits


PROVIDERS: dict[str, Callable[[str, int], list[PaperHit]]] = {
    "pubmed": query_pubmed,
    "arxiv": query_arxiv,
    "scholar": query_scholar,
}


def dedupe_hits(hits: Iterable[PaperHit]) -> list[PaperHit]:
    seen: set[str] = set()
    output: list[PaperHit] = []
    for hit in hits:
        key = (hit.doi or "") + "|" + re.sub(r"[^a-z0-9]+", "", (hit.title or "").lower())
        if key in seen:
            continue
        seen.add(key)
        output.append(hit)
    return output


def format_markdown(hits: list[PaperHit]) -> str:
    lines: list[str] = []
    for idx, hit in enumerate(hits, start=1):
        lines.append(f"## {idx}. {hit.title}")
        meta = [f"Source: {hit.provider}"]
        if hit.year:
            meta.append(f"Year: {hit.year}")
        if hit.is_preprint:
            meta.append("Preprint: yes")
        lines.append(" | ".join(meta))
        if hit.authors:
            lines.append(f"Authors: {hit.authors}")
        if hit.venue:
            lines.append(f"Venue: {hit.venue}")
        lines.append(f"Link: {hit.url}")
        if hit.doi:
            lines.append(f"DOI: {hit.doi}")
        if hit.abstract:
            lines.append(f"Abstract/Snippet: {hit.abstract}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Search literature from public scholarly sources.")
    parser.add_argument("--query", required=True, help="Search query.")
    parser.add_argument("--limit", type=int, default=5, help="Per-provider result limit.")
    parser.add_argument(
        "--providers",
        default="pubmed,europepmc,scholar,arxiv",
        help="Comma-separated providers: pubmed,europepmc,scholar,arxiv",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format.",
    )
    parser.add_argument(
        "--preprints-only",
        action="store_true",
        help="For Europe PMC, prefer preprints only.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.3,
        help="Delay between provider calls to stay polite.",
    )
    args = parser.parse_args()

    requested = [x.strip().lower() for x in args.providers.split(",") if x.strip()]
    all_hits: list[PaperHit] = []

    for provider in requested:
        try:
            if provider == "europepmc":
                hits = query_europe_pmc(args.query, args.limit, args.preprints_only)
            else:
                fn = PROVIDERS.get(provider)
                if not fn:
                    raise ValueError(f"Unsupported provider: {provider}")
                hits = fn(args.query, args.limit)
            all_hits.extend(hits)
        except Exception as exc:
            print(f"[warn] {provider}: {exc}", file=sys.stderr)
        time.sleep(max(args.sleep, 0.0))

    hits = dedupe_hits(all_hits)
    if args.format == "json":
        print(json.dumps([asdict(hit) for hit in hits], ensure_ascii=False, indent=2))
    else:
        print(format_markdown(hits), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
