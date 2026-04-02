import sys

from opendataloader_pdf_mcp.server import convert_pdf, extract_pdf, main

__all__ = ["extract_pdf", "convert_pdf", "main", "legacy_main"]


def legacy_main() -> int:
    print(
        "Warning: `pdf-analyzer-mcp` is deprecated and will be removed in v0.2.0. Use `opendataloader-pdf-mcp` instead.",
        file=sys.stderr,
    )
    return main()
