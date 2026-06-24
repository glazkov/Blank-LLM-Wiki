# llm-wiki-public workflow

## Purpose

Build a readable documentation site from a selected subset of an LLM Wiki. The internal wiki remains the durable working memory. The public site is a curated reader-facing surface.

## Page selection

Prefer pages that explain stable concepts, entities, systems, programs, databases, decisions, or flows.

Exclude by default:

- `raw/`;
- `logs/`;
- `outputs/`;
- `wiki/operations/`;
- transcripts and interviews;
- source notes that have not been synthesized;
- temporary hypotheses that are not marked as such.

## Editing expectations

If a source page is too internal, create or update a reader-facing page in `wiki/` first, then publish that page. Do not publish raw source material merely because it contains useful facts.

When a wiki link points to a non-public page, the builder turns it into plain text. If the missing target is important for readers, either add the target to `public-docs-manifest.json` or rewrite the sentence.

## Verification

Run:

```bash
make public-docs-validate
make public-docs-build
```

When local preview is needed, run:

```bash
make public-docs-serve
```

If a deployable archive is needed, run:

```bash
make public-docs-zip
```
