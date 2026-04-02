#!/usr/bin/env python3

from opendataloader_pdf_mcp.server import convert_pdf, extract_pdf, main

__all__ = ["extract_pdf", "convert_pdf", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
