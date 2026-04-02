---
name: opendataloader-pdf
description: MCP server for opendataloader-pdf that exposes extract_pdf and convert_pdf.
metadata:
  author: opendataloader-pdf-mcp contributors
  version: "0.1.0"
---

# OpenDataLoader PDF MCP

Use `extract_pdf` by default for compatibility with existing OpenCode setups.
Use `convert_pdf` when you want the upstream-aligned parameter names.

## Tools

### extract_pdf

```python
extract_pdf(
  file_path="/absolute/path/to/file.pdf",
  output_format="markdown"
)
```

### convert_pdf

```python
convert_pdf(
  input_path="/absolute/path/to/file.pdf",
  format="markdown"
)
```

Supported formats: `json`, `text`, `html`, `markdown`, `markdown-with-html`, `markdown-with-images`

Extra options passed through: `password`, `pages`, `sanitize`, `keep_line_breaks`, `detect_strikethrough`, `image_output`, `hybrid`
