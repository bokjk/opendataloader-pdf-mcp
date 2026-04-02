import warnings

from opendataloader_pdf_mcp import convert_pdf, extract_pdf, main

warnings.warn(
    "`pdf_analyzer` is deprecated and will be removed in v0.2.0. Use `opendataloader_pdf_mcp` instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["convert_pdf", "extract_pdf", "main"]
