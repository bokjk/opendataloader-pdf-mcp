#!/usr/bin/env python3

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_PY = ROOT / "server.py"
SAMPLE_PDF = ROOT / "tests" / "fixtures" / "sample.pdf"


def _send_recv(proc: subprocess.Popen[str], payload: dict[str, object]) -> dict[str, object]:
    assert proc.stdin is not None
    assert proc.stdout is not None
    assert proc.stderr is not None

    proc.stdin.write(__import__("json").dumps(payload) + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    if not line:
        stderr = proc.stderr.read()
        raise AssertionError(f"No response from server. stderr={stderr}")
    response = __import__("json").loads(line)
    assert isinstance(response, dict)
    return response


def _assert_standard_handshake(command: list[str] | None = None) -> None:
    proc = _start_server(command)
    try:
        _initialize_server(proc)
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
        assert "OpenDataLoader PDF MCP Test Document" in merged, "tools/call output missing fixture text"
    finally:
        _close_server(proc)


def _start_server(command: list[str] | None = None) -> subprocess.Popen[str]:
    launch_command = command or [sys.executable, str(SERVER_PY)]
    return subprocess.Popen(
        launch_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )


def _initialize_server(proc: subprocess.Popen[str]) -> None:
    init_resp = _send_recv(
        proc,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "pytest", "version": "0.1.0"},
            },
        },
    )
    assert "result" in init_resp, f"initialize failed: {init_resp}"
    assert proc.stdin is not None
    proc.stdin.write('{"jsonrpc": "2.0", "method": "notifications/initialized"}\n')
    proc.stdin.flush()


def _close_server(proc: subprocess.Popen[str]) -> None:
    if proc.stdin:
        proc.stdin.close()
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)


def test_tools_list_schema_content() -> None:
    proc = _start_server()
    try:
        _initialize_server(proc)
        list_resp = _send_recv(
            proc,
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        )
        assert "result" in list_resp, f"tools/list failed: {list_resp}"
        result = list_resp["result"]
        assert isinstance(result, dict), f"tools/list result missing/invalid: {list_resp}"
        tools = result.get("tools", [])
        assert isinstance(tools, list), f"tools list missing/invalid: {tools}"
        by_name = {
            tool.get("name"): tool
            for tool in tools
            if isinstance(tool, dict) and isinstance(tool.get("name"), str)
        }
        extract_tool = by_name.get("extract_pdf")
        convert_tool = by_name.get("convert_pdf")
        assert isinstance(extract_tool, dict), "extract_pdf missing from tools/list"
        assert isinstance(convert_tool, dict), "convert_pdf missing from tools/list"
        extract_props = extract_tool.get("inputSchema", {}).get("properties", {})
        convert_props = convert_tool.get("inputSchema", {}).get("properties", {})
        assert "file_path" in extract_props, f"extract_pdf schema missing file_path: {extract_props}"
        assert "output_format" in extract_props, (
            f"extract_pdf schema missing output_format: {extract_props}"
        )
        assert "input_path" in convert_props, f"convert_pdf schema missing input_path: {convert_props}"
        assert "format" in convert_props, f"convert_pdf schema missing format: {convert_props}"
    finally:
        _close_server(proc)


def test_tools_call_missing_file_returns_error_not_crash() -> None:
    proc = _start_server()
    try:
        _initialize_server(proc)
        call_resp = _send_recv(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "extract_pdf",
                    "arguments": {
                        "file_path": str(Path(__file__).resolve().parent / "fixtures" / "missing.pdf"),
                        "output_format": "markdown",
                    },
                },
            },
        )
        assert "result" in call_resp, f"Expected result response, got: {call_resp}"
        result = call_resp["result"]
        assert isinstance(result, dict), f"Expected dict result, got: {call_resp}"
        content_items = result.get("content", [])
        assert isinstance(content_items, list) and content_items, "Expected content in tools/call response"
        first_text = content_items[0].get("text", "")
        assert isinstance(first_text, str) and first_text.startswith("Error:"), (
            f"Expected Error text, got: {call_resp}"
        )

        list_resp = _send_recv(
            proc,
            {"jsonrpc": "2.0", "id": 4, "method": "tools/list", "params": {}},
        )
        assert "result" in list_resp, f"Server stopped responding after error: {list_resp}"
    finally:
        _close_server(proc)


def test_tools_call_unknown_tool_name() -> None:
    proc = _start_server()
    try:
        _initialize_server(proc)
        call_resp = _send_recv(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "nonexistent_tool", "arguments": {}},
            },
        )
        assert isinstance(call_resp, dict), f"Expected JSON object response, got: {call_resp}"
        assert "error" in call_resp or "result" in call_resp, (
            f"Expected valid JSON-RPC error/result response, got: {call_resp}"
        )

        list_resp = _send_recv(
            proc,
            {"jsonrpc": "2.0", "id": 6, "method": "tools/list", "params": {}},
        )
        assert "result" in list_resp, f"Server stopped responding after unknown tool: {list_resp}"
    finally:
        _close_server(proc)


def test_mcp_handshake_via_installed_entrypoint() -> None:
    executable_names = [
        "opendataloader-pdf-mcp.exe" if sys.platform == "win32" else "opendataloader-pdf-mcp",
        "pdf-analyzer-mcp.exe" if sys.platform == "win32" else "pdf-analyzer-mcp",
    ]

    entrypoint: Path | None = None
    for executable_name in executable_names:
        candidate = Path(sys.executable).with_name(executable_name)
        if candidate.exists():
            entrypoint = candidate
            break
        which_result = shutil.which(executable_name.replace(".exe", ""))
        if which_result is not None:
            entrypoint = Path(which_result)
            break

    assert entrypoint is not None, "Installed MCP entrypoint not found"
    _assert_standard_handshake([str(entrypoint)])


def test_convert_pdf_entrypoint_fixture_visibility() -> None:
    assert SAMPLE_PDF.exists(), f"Sample fixture missing: {SAMPLE_PDF}"
