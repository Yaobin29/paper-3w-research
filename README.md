# paper-3w-research

Search literature across `PubMed`, `Europe PMC`, `Google Scholar`, and `arXiv`, then turn each shortlisted paper into a fast, decision-friendly research note:

- `WHY`: why this paper matters
- `HOW`: how the work was done
- `WHAT`: what it actually showed or produced

`paper-3w-research` is a lightweight starter for researchers, builders, and agent workflows that need faster first-pass literature discovery without losing structure.

## Why this exists

Most literature search flows fail in one of two ways:

- they return a noisy pile of links with no reasoning structure
- they produce polished summaries that blur the paper's actual contribution

This repo is built around a simple rule: first find candidate papers from credible public sources, then summarize them in a frame that helps you compare research quickly and decide what to read next.

## Product snapshot

- Multi-source discovery: `PubMed`, `Europe PMC`, `Google Scholar`, `arXiv`
- Research-ready frame: `WHY / HOW / WHAT`
- Good fit for: biomedical, bioengineering, diagnostics, imaging, sensing, and ML-adjacent methods
- Usage modes: standalone Python script or agent skill starter
- Output style: compact shortlist for rapid triage, comparison, and review drafting

## What you get

- a reusable `SKILL.md` for agent workflows
- a small Python search script you can run directly
- source notes for provider interpretation
- a simple starter layout that is easy to fork and adapt

## What is inside

```text
.
├── SKILL.md
├── README.md
├── requirements.txt
├── agents/
│   └── openai.yaml
├── references/
│   ├── source-notes.md
│   └── why-how-what-frame.md
└── scripts/
    └── search_literature.py
```

## What this starter does well

- searches stable biomedical sources first
- uses Europe PMC to capture both literature and major biomedical preprints
- uses Google Scholar as a broad discovery layer
- adds arXiv for computational and ML-heavy work
- deduplicates obvious overlaps across providers
- gives you a compact shortlist that is easy to turn into a review brief

## Recommended use cases

- topic scanning before a grant or proposal
- fast comparison of several papers before deep reading
- finding both peer-reviewed and preprint work around a method
- turning an open-ended research question into a shortlist with consistent notes

## How it works

1. Convert a topic into one compact search query.
2. Search multiple public literature sources.
3. Deduplicate overlapping hits.
4. Keep papers with usable metadata, abstracts, or strong snippets.
5. Summarize each shortlisted paper in `WHY / HOW / WHAT`.
6. Synthesize cross-paper patterns, gaps, and next reading priorities.

## Quick start

1. Clone the repo.
2. Install dependencies.
3. Run the search script with your query.

```bash
git clone https://github.com/Yaobin29/paper-3w-research.git
cd paper-3w-research
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/search_literature.py \
  --query "silicon nanowire biosensor exosome detection pancreatic cancer" \
  --limit 5 \
  --providers pubmed,europepmc,scholar,arxiv \
  --format markdown
```

## Example output shape

```markdown
## Paper title
Source: pubmed | Year: 2024
Link: https://...

- WHY: This study addresses...
- HOW: The authors used...
- WHAT: They showed...
```

## Example prompt

```text
Use the paper-3w-research skill to search this topic across PubMed, Europe PMC, Google Scholar, and arXiv, then summarize each shortlisted paper by WHY, HOW, and WHAT.
```

## Using it as a Codex skill

You can point Codex or another agent to `SKILL.md` and ask it to:

- search a topic across PubMed, Google Scholar, and preprint sources
- shortlist the most relevant papers
- summarize each paper in a `WHY / HOW / WHAT` frame
- synthesize common themes, methodological differences, and unresolved gaps

## Notes on sources

- `PubMed`: best for stable biomedical indexing and metadata
- `Europe PMC`: strong for abstracts and biomedical preprints, including bioRxiv and medRxiv coverage via Europe PMC
- `Google Scholar`: broad but noisier; good for discovery, not your only evidence source
- `arXiv`: useful for computational, imaging, signal processing, and ML-heavy methods

## Limitations

- Google Scholar HTML may change and can be less stable than API-style sources
- some results may have incomplete metadata depending on the source
- this starter helps with discovery and first-pass comparison; it does not replace full paper reading

## Public starter design

This repository is intentionally kept small and portable:

- no private project config is required
- no Robin-specific output path is required
- the skill text is written to be reused in other agent setups
- the script can also be used on its own without any agent framework

## License

Released under the MIT License. See [LICENSE](LICENSE).
