---
name: paper-3w-research
description: Search biomedical and general research literature from Google Scholar, PubMed, and major preprint sources such as Europe PMC, bioRxiv, medRxiv, and arXiv, then present candidate papers in a WHY / HOW / WHAT frame. Use when the user wants literature discovery, topic scanning, paper comparison, or a structured explanation of what problem papers study, how they solve it, and what the results mean or still miss.
---

# Paper WHY HOW WHAT

Layer: `research`

Use this skill when the user wants to:

- search a topic across `Google Scholar`, `PubMed`, and preprint platforms,
- quickly compare several papers before deep reading,
- organize literature by:
  - `WHY`: why this work matters, what scientific or technical problem it targets,
  - `HOW`: how the authors approached it, what the technical idea or innovation is,
  - `WHAT`: what they produced or found, what it shows, and what gap remains.

## Default behavior

1. Run the bundled search script first to gather candidate papers.
2. Prefer `PubMed` and `Europe PMC` as stable evidence sources.
3. Use `Google Scholar` as a broad discovery supplement, not the only source.
4. If the user asks for preprints, include `Europe PMC` and `arXiv` by default.
5. Present the shortlist in Chinese unless the user asks otherwise.

## Fast path

Run:

```bash
python3 "$ROBIN_SKILLS_ROOT/paper-3w-research/scripts/search_literature.py" \
  --query "<topic or question>" \
  --limit 5 \
  --providers pubmed,europepmc,scholar,arxiv \
  --format markdown
```

Useful variants:

```bash
python3 "$ROBIN_SKILLS_ROOT/paper-3w-research/scripts/search_literature.py" \
  --query "<topic>" \
  --limit 8 \
  --providers pubmed,europepmc \
  --preprints-only \
  --format json
```

## Workflow

### 1. Clarify the search target

Convert the user request into one compact query string that captures:

- disease / biological system / material / device,
- intervention or method,
- application or readout,
- optional year window or article type.

If the user gives a mixed question, split it into subqueries before searching.

### 2. Retrieve candidates

Use `scripts/search_literature.py`.

Read `references/source-notes.md` only if you need source-specific interpretation details.

### 3. Rank and deduplicate

Prefer papers that have at least one of:

- abstract available,
- DOI or stable URL,
- clear method statement,
- explicit result claim.

Remove obvious duplicates across PubMed / Europe PMC / Scholar.

### 4. Build WHY / HOW / WHAT extraction

Read `references/why-how-what-frame.md` when you need the detailed rubric.

Minimum extraction per paper:

- `WHY`
  - what problem or bottleneck is being addressed,
  - why this problem matters,
  - what specific research question is being asked.
- `HOW`
  - main strategy,
  - experimental or computational route,
  - technical novelty or innovation point.
- `WHAT`
  - main result or artifact,
  - what the result implies,
  - remaining gap, limitation, or next-step question.

### 5. Response format

For each shortlisted paper, use this compact structure:

```markdown
## <paper title>
Source: <provider> | Year: <year> | Link: <url>

- WHY: ...
- HOW: ...
- WHAT: ...
```

When comparing multiple papers, add a final synthesis:

- common `WHY`,
- divergent `HOW`,
- strongest `WHAT`,
- unresolved global gap.

## Output routing

If the user asks to save a report, store it under:

- `$ROBIN_OUTPUTS_ROOT/paper-3w-research/<YYYY-MM-DD>/`

Preferred filename:

- `<YYYYMMDD_HHMM>__paper-3w-research__literature-brief__v01.md`

## References

- `references/why-how-what-frame.md`
- `references/source-notes.md`
- `scripts/search_literature.py`

## Completion contract

The task is complete when:

- at least one requested literature source has been searched,
- the returned shortlist includes clickable links,
- each shortlisted paper is framed with `WHY / HOW / WHAT`,
- if the user asked for it, a local report has been written to the correct outputs path.
