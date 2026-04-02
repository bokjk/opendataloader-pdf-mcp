# Changelog

## 0.1.0

- align wrapper behavior with `opendataloader-pdf` `v2.2.0`
- expose both `extract_pdf` and upstream-aligned `convert_pdf`
- support expanded upstream conversion options including `sanitize`, `detect_strikethrough`, and `image_dir`
- package the project as a shareable Python MCP server with `opendataloader-pdf-mcp` entry point
- add CI, license, skill file, build metadata, and public-sharing documentation
- rename the public package identity to `opendataloader-pdf-mcp` / `opendataloader_pdf_mcp`
- keep temporary compatibility shims for `pdf-analyzer-mcp`, `pdf_analyzer`, and local root entrypoints during the v0.1.x transition
- plan compatibility shim removal in `v0.2.0`
