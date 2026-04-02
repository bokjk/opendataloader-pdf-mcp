#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_PY = ROOT / "server.py"
SAMPLE_PDF = ROOT / "tests" / "fixtures" / "sample.pdf"


def _assert_successful_output(result: str) -> None:
    assert not result.startswith("Error:"), f"Got error: {result}"
    assert len(result.strip()) > 0, "Result is empty"


def run_test(name: str, fn: object) -> bool:
    try:
        callable_fn = fn
        assert callable(callable_fn)
        callable_fn()
        print(f"  [PASS] {name}")
        return True
    except AssertionError as exc:
        print(f"  [FAIL] {name}: {exc}")
        return False
    except Exception as exc:
        print(f"  [ERROR] {name}: {type(exc).__name__}: {exc}")
        return False


def test_import() -> None:
    import opendataloader_pdf_mcp.server  # noqa: F401


def test_extract_pdf_markdown() -> None:
    from opendataloader_pdf_mcp.server import extract_pdf

    result = extract_pdf(str(SAMPLE_PDF), "markdown")
    _assert_successful_output(result)
    assert "OpenDataLoader PDF MCP Test Document" in result, "Expected fixture text not found"


def test_extract_pdf_json() -> None:
    from opendataloader_pdf_mcp.server import extract_pdf

    result = extract_pdf(str(SAMPLE_PDF), "json")
    _assert_successful_output(result)
    parsed = json.loads(result)
    assert isinstance(parsed, dict | list), "JSON output is not structured"


def test_extract_pdf_text() -> None:
    from opendataloader_pdf_mcp.server import extract_pdf

    result = extract_pdf(str(SAMPLE_PDF), "text")
    _assert_successful_output(result)
    assert "OpenDataLoader PDF MCP Test Document" in result, "Expected fixture text not found"


def test_extract_pdf_html() -> None:
    from opendataloader_pdf_mcp.server import extract_pdf

    result = extract_pdf(str(SAMPLE_PDF), "html")
    _assert_successful_output(result)
    assert "<" in result, "Expected HTML-like output"
    assert "OpenDataLoader PDF MCP Test Document" in result, "Expected fixture text not found"


def test_extract_pdf_markdown_with_html() -> None:
    from opendataloader_pdf_mcp.server import extract_pdf

    result = extract_pdf(str(SAMPLE_PDF), "markdown-with-html")
    _assert_successful_output(result)
    assert "OpenDataLoader PDF MCP Test Document" in result, "Expected fixture text not found"


def test_extract_pdf_markdown_with_images() -> None:
    from opendataloader_pdf_mcp.server import extract_pdf

    result = extract_pdf(str(SAMPLE_PDF), "markdown-with-images")
    _assert_successful_output(result)


def test_extract_pdf_pages_param() -> None:
    from opendataloader_pdf_mcp.server import extract_pdf

    result = extract_pdf(str(SAMPLE_PDF), "markdown", pages="1")
    _assert_successful_output(result)
    assert "OpenDataLoader PDF MCP Test Document" in result, "Expected fixture text not found"


def test_extract_pdf_keep_line_breaks() -> None:
    from opendataloader_pdf_mcp.server import extract_pdf

    result = extract_pdf(str(SAMPLE_PDF), "text", keep_line_breaks=True)
    _assert_successful_output(result)


def test_extract_pdf_quoted_path() -> None:
    from opendataloader_pdf_mcp.server import extract_pdf

    result = extract_pdf(f'"{SAMPLE_PDF}"', "markdown")
    _assert_successful_output(result)
    assert "OpenDataLoader PDF MCP Test Document" in result, "Expected fixture text not found"


def test_extract_pdf_directory_path() -> None:
    from opendataloader_pdf_mcp.server import extract_pdf

    result = extract_pdf(str(SAMPLE_PDF.parent), "markdown")
    assert result.startswith("Error:"), f"Expected directory-path error, got: {result}"


def test_extract_pdf_invalid_format() -> None:
    from opendataloader_pdf_mcp.server import extract_pdf

    result = extract_pdf(str(SAMPLE_PDF), "yaml")
    assert result.startswith("Error:"), f"Expected unsupported-format error, got: {result}"
    assert "unsupported format" in result.lower(), (
        f"Expected unsupported-format message, got: {result}"
    )


def test_convert_pdf_alias() -> None:
    from opendataloader_pdf_mcp.server import convert_pdf

    result = convert_pdf(str(SAMPLE_PDF), "markdown")
    _assert_successful_output(result)
    assert "OpenDataLoader PDF MCP Test Document" in result, "Expected fixture text not found"


def test_convert_pdf_json_format() -> None:
    from opendataloader_pdf_mcp.server import convert_pdf

    result = convert_pdf(str(SAMPLE_PDF), "json")
    _assert_successful_output(result)
    parsed = json.loads(result)
    assert isinstance(parsed, dict | list), "JSON output is not structured"


def test_convert_pdf_text_format() -> None:
    from opendataloader_pdf_mcp.server import convert_pdf

    result = convert_pdf(str(SAMPLE_PDF), "text")
    _assert_successful_output(result)
    assert "OpenDataLoader PDF MCP Test Document" in result, "Expected fixture text not found"


def test_extract_pdf_nonexistent() -> None:
    from opendataloader_pdf_mcp.server import extract_pdf

    missing_path = ROOT / "tests" / "fixtures" / "missing.pdf"
    result = extract_pdf(str(missing_path), "markdown")
    assert "not found" in result.lower() or result.startswith("Error:"), (
        f"Expected missing-file error, got: {result[:120]}"
    )


def test_extract_pdf_empty_path() -> None:
    from opendataloader_pdf_mcp.server import extract_pdf

    result = extract_pdf("", "markdown")
    assert result.startswith("Error:") or "not found" in result.lower(), (
        f"Expected error for empty path, got: {result[:120]}"
    )


def test_extract_pdf_non_pdf() -> None:
    from opendataloader_pdf_mcp.server import extract_pdf

    result = extract_pdf(str(Path(__file__)), "markdown")
    assert result.startswith("Error:"), f"Expected non-PDF error, got: {result[:120]}"


def _send_recv(proc: subprocess.Popen[str], payload: dict[str, object]) -> dict[str, object]:
    assert proc.stdin is not None
    assert proc.stdout is not None
    assert proc.stderr is not None

    proc.stdin.write(json.dumps(payload) + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    if not line:
        stderr = proc.stderr.read()
        raise AssertionError(f"No response from server. stderr={stderr}")
    response = json.loads(line)
    assert isinstance(response, dict)
    return response


def test_mcp_handshake(command: list[str] | None = None) -> None:
    launch_command = command or [sys.executable, str(SERVER_PY)]
    proc = subprocess.Popen(
        launch_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    try:
        init_resp = _send_recv(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "0.1.0"},
                },
            },
        )
        assert "result" in init_resp, f"initialize failed: {init_resp}"
        init_result = init_resp["result"]
        assert isinstance(init_result, dict), f"initialize result missing/invalid: {init_resp}"
        capabilities = init_result.get("capabilities", {})
        assert isinstance(capabilities, dict), "initialize capabilities missing/invalid"

        assert proc.stdin is not None
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()

        list_resp = _send_recv(
            proc,
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        )
        assert "result" in list_resp, f"tools/list failed: {list_resp}"
        list_result = list_resp["result"]
        assert isinstance(list_result, dict), f"tools/list result missing/invalid: {list_resp}"
        tools = list_result.get("tools", [])
        assert isinstance(tools, list), f"tools list missing/invalid: {tools}"
        tool_names = [tool.get("name") for tool in tools if isinstance(tool, dict)]
        assert "extract_pdf" in tool_names, f"extract_pdf missing in tools/list: {tool_names}"
        assert "convert_pdf" in tool_names, f"convert_pdf missing in tools/list: {tool_names}"

        call_resp = _send_recv(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "extract_pdf",
                    "arguments": {
                        "file_path": str(SAMPLE_PDF),
                        "output_format": "markdown",
                    },
                },
            },
        )
        assert "result" in call_resp, f"tools/call failed: {call_resp}"
        call_result = call_resp["result"]
        assert isinstance(call_result, dict), f"tools/call result missing/invalid: {call_resp}"
        content_items = call_result.get("content", [])
        assert isinstance(content_items, list), f"content missing/invalid: {content_items}"
        text_chunks = [
            item.get("text", "") for item in content_items if isinstance(item, dict) and item.get("type") == "text"
        ]
        merged = "\n".join(text_chunks)
        assert "OpenDataLoader PDF MCP Test Document" in merged, "tools/call output does not contain fixture text"

        alias_resp = _send_recv(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "convert_pdf",
                    "arguments": {
                        "input_path": str(SAMPLE_PDF),
                        "format": "text",
                    },
                },
            },
        )
        assert "result" in alias_resp, f"convert_pdf tools/call failed: {alias_resp}"
        alias_result = alias_resp["result"]
        assert isinstance(alias_result, dict), f"convert_pdf result missing/invalid: {alias_resp}"
        alias_items = alias_result.get("content", [])
        assert isinstance(alias_items, list), f"alias content missing/invalid: {alias_items}"
        alias_text = "\n".join(
            item.get("text", "") for item in alias_items if isinstance(item, dict) and item.get("type") == "text"
        )
        assert "OpenDataLoader PDF MCP Test Document" in alias_text, (
            "convert_pdf tools/call output does not contain fixture text"
        )
    finally:
        if proc.stdin:
            proc.stdin.close()
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


def main() -> None:
    print("=" * 60)
    print("OpenDataLoader PDF MCP Server Tests")
    print("=" * 60)

    sys.path.insert(0, str(ROOT))

    from tests.test_helpers import (
        test_build_kwargs_markdown_with_images_defaults_embedded,
        test_build_kwargs_markdown_with_images_explicit_override,
        test_build_kwargs_minimal,
        test_build_kwargs_optional_passthrough,
        test_error_corrupt,
        test_error_damage,
        test_error_encrypted,
        test_error_generic,
        test_error_invalid,
        test_error_password,
        test_normalize_path_mixed,
        test_normalize_path_strips_double_quotes,
        test_normalize_path_strips_single_quotes,
        test_normalize_path_strips_whitespace,
        test_read_fallback_when_stem_mismatch,
        test_read_primary_filename,
        test_read_raises_if_no_files,
        test_read_raises_if_no_matching_extension,
        test_validate_directory_path,
        test_validate_empty_string,
        test_validate_file_too_large,
        test_validate_invalid_signature,
        test_validate_missing_file,
        test_validate_non_pdf_extension,
    )
    from tests.test_mcp_protocol import (
        test_mcp_handshake_via_installed_entrypoint,
        test_tools_call_missing_file_returns_error_not_crash,
        test_tools_call_unknown_tool_name,
        test_tools_list_schema_content,
    )

    unit_tests = [
        ("Import server module", test_import),
        ("normalize_path: strips whitespace", test_normalize_path_strips_whitespace),
        ("normalize_path: strips double quotes", test_normalize_path_strips_double_quotes),
        ("normalize_path: strips single quotes", test_normalize_path_strips_single_quotes),
        ("normalize_path: mixed trimming", test_normalize_path_mixed),
        ("validate_pdf_path: empty string", test_validate_empty_string),
        ("validate_pdf_path: missing file", test_validate_missing_file),
        ("validate_pdf_path: directory path", test_validate_directory_path),
        ("validate_pdf_path: non-PDF extension", test_validate_non_pdf_extension),
        ("validate_pdf_path: invalid signature", test_validate_invalid_signature),
        ("validate_pdf_path: file too large", test_validate_file_too_large),
        ("build_convert_kwargs: minimal", test_build_kwargs_minimal),
        (
            "build_convert_kwargs: markdown-with-images defaults embedded",
            test_build_kwargs_markdown_with_images_defaults_embedded,
        ),
        (
            "build_convert_kwargs: explicit image_output override",
            test_build_kwargs_markdown_with_images_explicit_override,
        ),
        ("build_convert_kwargs: optional passthrough", test_build_kwargs_optional_passthrough),
        ("read_output_file: primary filename", test_read_primary_filename),
        ("read_output_file: fallback stem mismatch", test_read_fallback_when_stem_mismatch),
        ("read_output_file: no files", test_read_raises_if_no_files),
        ("read_output_file: no matching extension", test_read_raises_if_no_matching_extension),
        ("handle_conversion_error: password", test_error_password),
        ("handle_conversion_error: encrypted", test_error_encrypted),
        ("handle_conversion_error: corrupt", test_error_corrupt),
        ("handle_conversion_error: invalid", test_error_invalid),
        ("handle_conversion_error: damage", test_error_damage),
        ("handle_conversion_error: generic", test_error_generic),
        ("extract_pdf: markdown format", test_extract_pdf_markdown),
        ("extract_pdf: json format", test_extract_pdf_json),
        ("extract_pdf: text format", test_extract_pdf_text),
        ("extract_pdf: html format", test_extract_pdf_html),
        ("extract_pdf: markdown-with-html format", test_extract_pdf_markdown_with_html),
        ("extract_pdf: markdown-with-images format", test_extract_pdf_markdown_with_images),
        ("extract_pdf: pages param", test_extract_pdf_pages_param),
        ("extract_pdf: keep_line_breaks param", test_extract_pdf_keep_line_breaks),
        ("extract_pdf: quoted path", test_extract_pdf_quoted_path),
        ("extract_pdf: directory path -> error", test_extract_pdf_directory_path),
        ("extract_pdf: invalid format -> error", test_extract_pdf_invalid_format),
        ("convert_pdf alias: markdown format", test_convert_pdf_alias),
        ("convert_pdf alias: json format", test_convert_pdf_json_format),
        ("convert_pdf alias: text format", test_convert_pdf_text_format),
        ("extract_pdf: nonexistent file -> error", test_extract_pdf_nonexistent),
        ("extract_pdf: empty path -> error", test_extract_pdf_empty_path),
        ("extract_pdf: non-PDF file -> error", test_extract_pdf_non_pdf),
    ]

    print("\n[Unit Tests]")
    unit_results = [run_test(name, fn) for name, fn in unit_tests]

    print("\n[MCP Protocol Tests]")
    mcp_tests = [
        ("MCP stdio: initialize + tools/list + tools/call", test_mcp_handshake),
        ("MCP stdio: tools/list schema", test_tools_list_schema_content),
        (
            "MCP stdio: missing file returns error without crash",
            test_tools_call_missing_file_returns_error_not_crash,
        ),
        ("MCP stdio: unknown tool name does not crash", test_tools_call_unknown_tool_name),
        (
            "MCP installed entrypoint: initialize + tools/list + tools/call",
            test_mcp_handshake_via_installed_entrypoint,
        ),
    ]
    mcp_results = [run_test(name, fn) for name, fn in mcp_tests]

    total = len(unit_results) + len(mcp_results)
    passed = sum(unit_results) + sum(mcp_results)

    print(f"\n{'=' * 60}")
    print(f"Results: {passed}/{total} passed")

    if passed == total:
        print("All tests PASSED")
        sys.exit(0)

    print("Some tests FAILED")
    sys.exit(1)


if __name__ == "__main__":
    main()
