#!/usr/bin/env python3

import tempfile
from pathlib import Path
from typing import TypedDict

import opendataloader_pdf
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("opendataloader-pdf")

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024
FORMAT_EXTENSION_MAP = {
    "json": ".json",
    "text": ".txt",
    "html": ".html",
    "markdown": ".md",
    "markdown-with-html": ".md",
    "markdown-with-images": ".md",
}


class ConvertKwargs(TypedDict, total=False):
    input_path: str
    output_dir: str
    format: str
    quiet: bool
    password: str
    pages: str
    keep_line_breaks: bool
    sanitize: bool
    content_safety_off: str
    replace_invalid_chars: str
    use_struct_tree: bool
    table_method: str
    reading_order: str
    markdown_page_separator: str
    text_page_separator: str
    html_page_separator: str
    image_output: str
    image_format: str
    include_header_footer: bool
    detect_strikethrough: bool
    hybrid: str
    hybrid_mode: str
    hybrid_url: str
    hybrid_timeout: str
    hybrid_fallback: bool
    image_dir: str


def _normalize_path(file_path: str) -> str:
    return file_path.strip().strip('"').strip("'")


def _validate_pdf_path(file_path: str) -> Path:
    normalized = _normalize_path(file_path)
    if not normalized:
        raise ValueError("File path is empty")

    path = Path(normalized).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    file_size = path.stat().st_size
    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"File too large: {file_size / 1024 / 1024:.1f}MB (max 50MB)"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF file: {path.name}")

    try:
        with path.open("rb") as file_obj:
            signature = file_obj.read(4)
    except OSError as exc:
        raise ValueError(f"Cannot read file: {exc}") from exc

    if signature != b"%PDF":
        raise ValueError("File does not appear to be a valid PDF (invalid signature)")

    return path


def _build_convert_kwargs(
    *,
    input_file: Path,
    output_dir: str,
    format: str,
    password: str | None,
    pages: str | None,
    keep_line_breaks: bool,
    sanitize: bool,
    content_safety_off: str | None,
    replace_invalid_chars: str | None,
    use_struct_tree: bool,
    table_method: str | None,
    reading_order: str | None,
    markdown_page_separator: str | None,
    text_page_separator: str | None,
    html_page_separator: str | None,
    image_output: str | None,
    image_format: str | None,
    include_header_footer: bool,
    detect_strikethrough: bool,
    hybrid: str | None,
    hybrid_mode: str | None,
    hybrid_url: str | None,
    hybrid_timeout: str | None,
    hybrid_fallback: bool,
    image_dir: str | None,
) -> ConvertKwargs:
    kwargs: ConvertKwargs = {
        "input_path": str(input_file),
        "output_dir": output_dir,
        "format": format,
        "quiet": True,
    }

    if password is not None:
        kwargs["password"] = password
    if pages is not None:
        kwargs["pages"] = pages
    if keep_line_breaks:
        kwargs["keep_line_breaks"] = True
    if sanitize:
        kwargs["sanitize"] = True
    if content_safety_off is not None:
        kwargs["content_safety_off"] = content_safety_off
    if replace_invalid_chars is not None:
        kwargs["replace_invalid_chars"] = replace_invalid_chars
    if use_struct_tree:
        kwargs["use_struct_tree"] = True
    if table_method is not None:
        kwargs["table_method"] = table_method
    if reading_order is not None:
        kwargs["reading_order"] = reading_order
    if markdown_page_separator is not None:
        kwargs["markdown_page_separator"] = markdown_page_separator
    if text_page_separator is not None:
        kwargs["text_page_separator"] = text_page_separator
    if html_page_separator is not None:
        kwargs["html_page_separator"] = html_page_separator
    if format == "markdown-with-images" and image_output is None:
        kwargs["image_output"] = "embedded"
    elif image_output is not None:
        kwargs["image_output"] = image_output
    if image_format is not None:
        kwargs["image_format"] = image_format
    if include_header_footer:
        kwargs["include_header_footer"] = True
    if detect_strikethrough:
        kwargs["detect_strikethrough"] = True
    if hybrid is not None:
        kwargs["hybrid"] = hybrid
    if hybrid_mode is not None:
        kwargs["hybrid_mode"] = hybrid_mode
    if hybrid_url is not None:
        kwargs["hybrid_url"] = hybrid_url
    if hybrid_timeout is not None:
        kwargs["hybrid_timeout"] = hybrid_timeout
    if hybrid_fallback:
        kwargs["hybrid_fallback"] = True
    if image_dir is not None:
        kwargs["image_dir"] = image_dir

    return kwargs


def _read_output_file(tmp_dir: str, input_file: Path, format: str) -> str:
    extension = FORMAT_EXTENSION_MAP[format]
    output_file = Path(tmp_dir) / f"{input_file.stem}{extension}"

    if not output_file.is_file():
        files = [file for file in Path(tmp_dir).iterdir() if file.is_file()]
        if not files:
            raise RuntimeError("Conversion completed but no output file was generated.")

        matching_files = sorted(file for file in files if file.suffix == extension)
        if not matching_files:
            raise RuntimeError(
                f"Conversion completed but no '{extension}' output file was generated."
            )
        output_file = matching_files[0]

    return output_file.read_text(encoding="utf-8", errors="replace")


def _convert_pdf_content(
    *,
    file_path: str,
    format: str = "markdown",
    password: str | None = None,
    pages: str | None = None,
    keep_line_breaks: bool = False,
    sanitize: bool = False,
    content_safety_off: str | None = None,
    replace_invalid_chars: str | None = None,
    use_struct_tree: bool = False,
    table_method: str | None = None,
    reading_order: str | None = None,
    markdown_page_separator: str | None = None,
    text_page_separator: str | None = None,
    html_page_separator: str | None = None,
    image_output: str | None = None,
    image_format: str | None = None,
    include_header_footer: bool = False,
    detect_strikethrough: bool = False,
    hybrid: str | None = None,
    hybrid_mode: str | None = None,
    hybrid_url: str | None = None,
    hybrid_timeout: str | None = None,
    hybrid_fallback: bool = False,
    image_dir: str | None = None,
) -> str:
    input_file = _validate_pdf_path(file_path)
    normalized_format = format.lower().strip()

    if normalized_format not in FORMAT_EXTENSION_MAP:
        supported_formats = ", ".join(FORMAT_EXTENSION_MAP)
        raise ValueError(
            f"Unsupported format: {normalized_format!r}. Supported formats: {supported_formats}"
        )

    with tempfile.TemporaryDirectory() as tmp_dir:
        kwargs = _build_convert_kwargs(
            input_file=input_file,
            output_dir=tmp_dir,
            format=normalized_format,
            password=password,
            pages=pages,
            keep_line_breaks=keep_line_breaks,
            sanitize=sanitize,
            content_safety_off=content_safety_off,
            replace_invalid_chars=replace_invalid_chars,
            use_struct_tree=use_struct_tree,
            table_method=table_method,
            reading_order=reading_order,
            markdown_page_separator=markdown_page_separator,
            text_page_separator=text_page_separator,
            html_page_separator=html_page_separator,
            image_output=image_output,
            image_format=image_format,
            include_header_footer=include_header_footer,
            detect_strikethrough=detect_strikethrough,
            hybrid=hybrid,
            hybrid_mode=hybrid_mode,
            hybrid_url=hybrid_url,
            hybrid_timeout=hybrid_timeout,
            hybrid_fallback=hybrid_fallback,
            image_dir=image_dir,
        )
        opendataloader_pdf.convert(**kwargs)
        return _read_output_file(tmp_dir, input_file, normalized_format)


def _handle_conversion_error(exc: Exception) -> str:
    message = str(exc)
    lowered = message.lower()

    if "password" in lowered or "encrypted" in lowered:
        return "Error: PDF is password-protected. Cannot extract content."
    if "corrupt" in lowered or "invalid" in lowered or "damage" in lowered:
        return f"Error: PDF appears to be corrupted or invalid: {message}"
    return f"Error: {message}"


@mcp.tool(name="extract_pdf")
def extract_pdf(
    file_path: str,
    output_format: str = "markdown",
    password: str | None = None,
    pages: str | None = None,
    keep_line_breaks: bool = False,
    sanitize: bool = False,
    content_safety_off: str | None = None,
    replace_invalid_chars: str | None = None,
    use_struct_tree: bool = False,
    table_method: str | None = None,
    reading_order: str | None = None,
    markdown_page_separator: str | None = None,
    text_page_separator: str | None = None,
    html_page_separator: str | None = None,
    image_output: str | None = None,
    image_format: str | None = None,
    include_header_footer: bool = False,
    detect_strikethrough: bool = False,
    hybrid: str | None = None,
    hybrid_mode: str | None = None,
    hybrid_url: str | None = None,
    hybrid_timeout: str | None = None,
    hybrid_fallback: bool = False,
    image_dir: str | None = None,
) -> str:
    try:
        content = _convert_pdf_content(
            file_path=file_path,
            format=output_format,
            password=password,
            pages=pages,
            keep_line_breaks=keep_line_breaks,
            sanitize=sanitize,
            content_safety_off=content_safety_off,
            replace_invalid_chars=replace_invalid_chars,
            use_struct_tree=use_struct_tree,
            table_method=table_method,
            reading_order=reading_order,
            markdown_page_separator=markdown_page_separator,
            text_page_separator=text_page_separator,
            html_page_separator=html_page_separator,
            image_output=image_output,
            image_format=image_format,
            include_header_footer=include_header_footer,
            detect_strikethrough=detect_strikethrough,
            hybrid=hybrid,
            hybrid_mode=hybrid_mode,
            hybrid_url=hybrid_url,
            hybrid_timeout=hybrid_timeout,
            hybrid_fallback=hybrid_fallback,
            image_dir=image_dir,
        )
    except Exception as exc:
        return _handle_conversion_error(exc)

    if not content.strip():
        return (
            "Warning: Extraction completed but result is empty. "
            "The PDF may contain no extractable text (scanned/image-only PDF)."
        )

    return content


@mcp.tool(name="convert_pdf")
def convert_pdf(
    input_path: str,
    format: str = "markdown",
    password: str | None = None,
    pages: str | None = None,
    keep_line_breaks: bool = False,
    sanitize: bool = False,
    content_safety_off: str | None = None,
    replace_invalid_chars: str | None = None,
    use_struct_tree: bool = False,
    table_method: str | None = None,
    reading_order: str | None = None,
    markdown_page_separator: str | None = None,
    text_page_separator: str | None = None,
    html_page_separator: str | None = None,
    image_output: str | None = None,
    image_format: str | None = None,
    include_header_footer: bool = False,
    detect_strikethrough: bool = False,
    hybrid: str | None = None,
    hybrid_mode: str | None = None,
    hybrid_url: str | None = None,
    hybrid_timeout: str | None = None,
    hybrid_fallback: bool = False,
    image_dir: str | None = None,
) -> str:
    return extract_pdf(
        file_path=input_path,
        output_format=format,
        password=password,
        pages=pages,
        keep_line_breaks=keep_line_breaks,
        sanitize=sanitize,
        content_safety_off=content_safety_off,
        replace_invalid_chars=replace_invalid_chars,
        use_struct_tree=use_struct_tree,
        table_method=table_method,
        reading_order=reading_order,
        markdown_page_separator=markdown_page_separator,
        text_page_separator=text_page_separator,
        html_page_separator=html_page_separator,
        image_output=image_output,
        image_format=image_format,
        include_header_footer=include_header_footer,
        detect_strikethrough=detect_strikethrough,
        hybrid=hybrid,
        hybrid_mode=hybrid_mode,
        hybrid_url=hybrid_url,
        hybrid_timeout=hybrid_timeout,
        hybrid_fallback=hybrid_fallback,
        image_dir=image_dir,
    )


def main() -> int:
    mcp.run()
    return 0
