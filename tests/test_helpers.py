#!/usr/bin/env python3

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from opendataloader_pdf_mcp.server import (
    _build_convert_kwargs,
    _handle_conversion_error,
    _normalize_path,
    _read_output_file,
    _validate_pdf_path,
)


def _write_file(path: Path, data: bytes) -> Path:
    path.write_bytes(data)
    return path


def test_normalize_path_strips_whitespace() -> None:
    assert _normalize_path("  /a/b.pdf  ") == "/a/b.pdf"


def test_normalize_path_strips_double_quotes() -> None:
    assert _normalize_path('"path.pdf"') == "path.pdf"


def test_normalize_path_strips_single_quotes() -> None:
    assert _normalize_path("'path.pdf'") == "path.pdf"


def test_normalize_path_mixed() -> None:
    assert _normalize_path('  "path.pdf" ') == "path.pdf"


def test_validate_empty_string() -> None:
    try:
        _validate_pdf_path("")
    except ValueError as exc:
        assert "empty" in str(exc).lower()
        return
    raise AssertionError("Expected ValueError for empty path")


def test_validate_missing_file() -> None:
    try:
        _validate_pdf_path("missing-file.pdf")
    except FileNotFoundError:
        return
    raise AssertionError("Expected FileNotFoundError for missing file")


def test_validate_directory_path() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            _validate_pdf_path(tmp_dir)
        except ValueError as exc:
            assert "not a file" in str(exc).lower()
            return
    raise AssertionError("Expected ValueError for directory path")


def test_validate_non_pdf_extension() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = _write_file(Path(tmp_dir) / "file.txt", b"%PDF pretend")
        try:
            _validate_pdf_path(str(path))
        except ValueError as exc:
            assert "not a pdf" in str(exc).lower()
            return
    raise AssertionError("Expected ValueError for non-PDF extension")


def test_validate_invalid_signature() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = _write_file(Path(tmp_dir) / "file.pdf", b"XXXX invalid")
        try:
            _validate_pdf_path(str(path))
        except ValueError as exc:
            assert "invalid signature" in str(exc).lower()
            return
    raise AssertionError("Expected ValueError for invalid PDF signature")


def test_validate_file_too_large() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = _write_file(Path(tmp_dir) / "file.pdf", b"%PDF tiny")
        fake_stat = Path(path).stat()
        oversized = os.stat_result(fake_stat[0:6] + (51 * 1024 * 1024,) + fake_stat[7:10])
        with patch("pathlib.Path.stat", return_value=oversized):
            try:
                _validate_pdf_path(str(path))
            except ValueError as exc:
                assert "too large" in str(exc).lower()
                return
    raise AssertionError("Expected ValueError for oversized file")


def test_build_kwargs_minimal() -> None:
    kwargs = _build_convert_kwargs(
        input_file=Path("sample.pdf"),
        output_dir="out",
        format="markdown",
        password=None,
        pages=None,
        keep_line_breaks=False,
        sanitize=False,
        content_safety_off=None,
        replace_invalid_chars=None,
        use_struct_tree=False,
        table_method=None,
        reading_order=None,
        markdown_page_separator=None,
        text_page_separator=None,
        html_page_separator=None,
        image_output=None,
        image_format=None,
        include_header_footer=False,
        detect_strikethrough=False,
        hybrid=None,
        hybrid_mode=None,
        hybrid_url=None,
        hybrid_timeout=None,
        hybrid_fallback=False,
        image_dir=None,
    )
    assert kwargs == {
        "input_path": "sample.pdf",
        "output_dir": "out",
        "format": "markdown",
        "quiet": True,
    }


def test_build_kwargs_markdown_with_images_defaults_embedded() -> None:
    kwargs = _build_convert_kwargs(
        input_file=Path("sample.pdf"),
        output_dir="out",
        format="markdown-with-images",
        password=None,
        pages=None,
        keep_line_breaks=False,
        sanitize=False,
        content_safety_off=None,
        replace_invalid_chars=None,
        use_struct_tree=False,
        table_method=None,
        reading_order=None,
        markdown_page_separator=None,
        text_page_separator=None,
        html_page_separator=None,
        image_output=None,
        image_format=None,
        include_header_footer=False,
        detect_strikethrough=False,
        hybrid=None,
        hybrid_mode=None,
        hybrid_url=None,
        hybrid_timeout=None,
        hybrid_fallback=False,
        image_dir=None,
    )
    assert kwargs.get("image_output") == "embedded"


def test_build_kwargs_markdown_with_images_explicit_override() -> None:
    kwargs = _build_convert_kwargs(
        input_file=Path("sample.pdf"),
        output_dir="out",
        format="markdown-with-images",
        password=None,
        pages=None,
        keep_line_breaks=False,
        sanitize=False,
        content_safety_off=None,
        replace_invalid_chars=None,
        use_struct_tree=False,
        table_method=None,
        reading_order=None,
        markdown_page_separator=None,
        text_page_separator=None,
        html_page_separator=None,
        image_output="file",
        image_format=None,
        include_header_footer=False,
        detect_strikethrough=False,
        hybrid=None,
        hybrid_mode=None,
        hybrid_url=None,
        hybrid_timeout=None,
        hybrid_fallback=False,
        image_dir=None,
    )
    assert kwargs.get("image_output") == "file"


def test_build_kwargs_optional_passthrough() -> None:
    kwargs = _build_convert_kwargs(
        input_file=Path("sample.pdf"),
        output_dir="out",
        format="markdown",
        password="pw",
        pages="1-2",
        keep_line_breaks=True,
        sanitize=True,
        content_safety_off="emails,urls",
        replace_invalid_chars="?",
        use_struct_tree=True,
        table_method="lattice",
        reading_order="natural",
        markdown_page_separator="---",
        text_page_separator="TXT",
        html_page_separator="HTML",
        image_output="embedded",
        image_format="png",
        include_header_footer=True,
        detect_strikethrough=True,
        hybrid="ocr",
        hybrid_mode="remote",
        hybrid_url="https://example.com",
        hybrid_timeout="0",
        hybrid_fallback=True,
        image_dir="images",
    )
    assert kwargs.get("password") == "pw"
    assert kwargs.get("pages") == "1-2"
    assert kwargs.get("keep_line_breaks") is True
    assert kwargs.get("sanitize") is True
    assert kwargs.get("table_method") == "lattice"
    assert kwargs.get("hybrid") == "ocr"
    assert kwargs.get("image_dir") == "images"


def test_read_primary_filename() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "sample.md"
        path.write_text("primary output", encoding="utf-8")
        result = _read_output_file(tmp_dir, Path("sample.pdf"), "markdown")
        assert result == "primary output"


def test_read_fallback_when_stem_mismatch() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        (Path(tmp_dir) / "z.md").write_text("later", encoding="utf-8")
        (Path(tmp_dir) / "a.md").write_text("first", encoding="utf-8")
        result = _read_output_file(tmp_dir, Path("sample.pdf"), "markdown")
        assert result == "first"


def test_read_raises_if_no_files() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            _read_output_file(tmp_dir, Path("sample.pdf"), "markdown")
        except RuntimeError as exc:
            assert "no output file" in str(exc).lower()
            return
    raise AssertionError("Expected RuntimeError when no files exist")


def test_read_raises_if_no_matching_extension() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        (Path(tmp_dir) / "output.txt").write_text("wrong extension", encoding="utf-8")
        try:
            _read_output_file(tmp_dir, Path("sample.pdf"), "markdown")
        except RuntimeError as exc:
            assert ".md" in str(exc)
            return
    raise AssertionError("Expected RuntimeError when no matching extension exists")


def test_error_password() -> None:
    assert _handle_conversion_error(Exception("Password required")) == (
        "Error: PDF is password-protected. Cannot extract content."
    )


def test_error_encrypted() -> None:
    assert _handle_conversion_error(Exception("File is encrypted")) == (
        "Error: PDF is password-protected. Cannot extract content."
    )


def test_error_corrupt() -> None:
    result = _handle_conversion_error(Exception("Corrupt structure"))
    assert result.startswith("Error: PDF appears to be corrupted or invalid:")


def test_error_invalid() -> None:
    result = _handle_conversion_error(Exception("Invalid object"))
    assert result.startswith("Error: PDF appears to be corrupted or invalid:")


def test_error_damage() -> None:
    result = _handle_conversion_error(Exception("File damage detected"))
    assert result.startswith("Error: PDF appears to be corrupted or invalid:")


def test_error_generic() -> None:
    assert _handle_conversion_error(Exception("Something else")) == "Error: Something else"
