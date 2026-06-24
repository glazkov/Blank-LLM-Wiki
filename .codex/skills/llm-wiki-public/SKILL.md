---
name: llm-wiki-public
description: Use when the user asks to publish, package, export, or turn selected LLM Wiki Markdown pages into readable public documentation using an allowlist manifest, MkDocs Material, and the public-docs layer.
---

# llm-wiki-public

Use this skill to turn selected pages from an LLM Wiki project into public human-readable documentation.

## Workflow

1. Start from `wiki/index.md`, `wiki/overview.md`, and `wiki/operations/project-status.md`.
2. Identify the intended reader and scope of the public documentation.
3. Build or update `public-docs-manifest.json` as an allowlist.
4. Do not publish `raw/`, `logs/`, `outputs/`, `wiki/operations/`, interviews, transcripts, or internal process notes unless explicitly requested.
5. Run `make public-docs-validate`.
6. Run `make public-docs-build`.
7. If requested, run `make public-docs-zip`.
8. Update persistent project artifacts according to the local `AGENTS.md`.

Read `references/workflow.md` for detailed workflow guidance.
Read `references/manifest.md` when creating or reviewing `public-docs-manifest.json`.
