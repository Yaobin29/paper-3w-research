# paper-3w-research

`paper-3w-research` is a lightweight research skill starter for literature discovery across `PubMed`, `Europe PMC`, `Google Scholar`, and `arXiv`, followed by a structured summary frame:

- `WHY`: why the paper matters, what problem it targets, and why that problem is important
- `HOW`: how the authors approached the problem, including the main method or innovation
- `WHAT`: what they found, built, or demonstrated, plus the remaining gap

This repo is designed for people who want a reusable prompt-and-script starter for biomedical and adjacent technical literature reviews.

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

## Using it as a Codex skill

You can point Codex or another agent to `SKILL.md` and ask it to:

- search a topic across PubMed, Google Scholar, and preprint sources
- shortlist the most relevant papers
- summarize each paper in a `WHY / HOW / WHAT` frame
- synthesize common themes, methodological differences, and unresolved gaps

Suggested prompt:

```text
Use the paper-3w-research skill to search this topic across PubMed, Google Scholar, Europe PMC, and arXiv, then summarize each shortlisted paper by WHY, HOW, and WHAT.
```

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

No license file is included yet. Add one before broader reuse if you want to define sharing terms explicitly.
