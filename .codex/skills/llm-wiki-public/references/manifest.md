# public-docs-manifest.json

The manifest is an allowlist. Only listed pages are published.

## Minimal shape

```json
{
  "site": {
    "name": "Public Documentation",
    "description": "Public documentation generated from selected LLM Wiki pages"
  },
  "pages": [
    {
      "source": "wiki/overview.md",
      "dest": "index.md"
    }
  ]
}
```

## Rules

- `source` is relative to the project root.
- `dest` is relative to `public-docs/build/docs`.
- Markdown sources must map to Markdown destinations.
- Destinations must not be absolute and must not contain `..`.
- Duplicate destinations are invalid.
- `raw/`, `logs/`, and `outputs/` are blocked.
- `wiki/operations/` is blocked unless the manifest explicitly sets `"allowOperations": true`.

## Example

```json
{
  "site": {
    "name": "Internal Developer Docs",
    "description": "Selected system documentation"
  },
  "pages": [
    {"source": "wiki/overview.md", "dest": "index.md"},
    {"source": "wiki/concepts/system-map.md", "dest": "concepts/system-map.md"},
    {"source": "wiki/entities/main-product.md", "dest": "entities/main-product.md"}
  ]
}
```
