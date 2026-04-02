# OpenDataLoader PDF MCP

Shareable Python MCP server for PDF extraction built on `opendataloader-pdf`.

## Quick Start (Korean)

이 프로젝트는 나중에 GitHub 주소나 PyPI 패키지 이름만으로 쉽게 설치할 수 있게 만들어져 있습니다.

### 1) GitHub 주소로 바로 설치

공개 저장소를 만든 뒤에는 보통 아래처럼 설치하게 됩니다:

```bash
pip install "git+https://github.com/<OWNER>/<REPO>.git"
```

예를 들어 공개 주소가 `https://github.com/example/opendataloader-pdf-mcp` 라면:

```bash
pip install "git+https://github.com/example/opendataloader-pdf-mcp.git"
```

### 2) PyPI에 올린 뒤 설치

PyPI에 배포하면 더 간단하게 설치할 수 있습니다:

```bash
pip install opendataloader-pdf-mcp
```

### 3) 설치 후 실행

```bash
opendataloader-pdf-mcp
```

### 4) OpenCode에 연결

설치가 끝나면 OpenCode에서는 설치된 명령만 호출하면 됩니다:

```json
{
  "mcp": {
    "opendataloader-pdf": {
      "command": ["opendataloader-pdf-mcp"],
      "enabled": true,
      "type": "local"
    }
  }
}
```

### 5) 꼭 필요한 준비물

- Python 3.10+
- Java 11+

이 프로젝트는 `JAVA_HOME`을 강제로 설정하지 않습니다. 대상 머신에서 Java가 `PATH` 또는 `JAVA_HOME`으로 잡혀 있어야 합니다.

---

## Quick Start (English)

This project is designed so users can install it the easy way later — either from a GitHub URL or from PyPI.

### 1) Install directly from a GitHub URL

Once the repository is public, users can install it like this:

```bash
pip install "git+https://github.com/<OWNER>/<REPO>.git"
```

For example, if the public repository is `https://github.com/example/opendataloader-pdf-mcp`:

```bash
pip install "git+https://github.com/example/opendataloader-pdf-mcp.git"
```

### 2) Install from PyPI

If you publish the package to PyPI, users can install it like a normal package:

```bash
pip install opendataloader-pdf-mcp
```

### 3) Run the MCP server

```bash
opendataloader-pdf-mcp
```

### 4) Connect it to OpenCode

After installation, OpenCode can launch the installed command directly:

```json
{
  "mcp": {
    "opendataloader-pdf": {
      "command": ["opendataloader-pdf-mcp"],
      "enabled": true,
      "type": "local"
    }
  }
}
```

### 5) Requirements

- Python 3.10+
- Java 11+

This project does not set `JAVA_HOME` for users. Java must already be available through `PATH` or `JAVA_HOME` on the target machine.

## Install from source

```bash
python -m pip install -e .
```

This is mainly for local development. For real users, the recommended flows are:

- `pip install "git+https://github.com/<OWNER>/<REPO>.git"`
- `pip install opendataloader-pdf-mcp` (after PyPI publishing)

If you publish this package to a package index later, users can install it like a normal MCP package:

```bash
pip install opendataloader-pdf-mcp
```

For packaging and release work:

```bash
python -m pip install -r requirements-dev.txt
```

## Run the server

After installation, the console entry point is:

```bash
opendataloader-pdf-mcp
```

You can also run it with Python directly:

```bash
python -m opendataloader_pdf_mcp
```

## Exposed tools

### `extract_pdf`

Compatibility-first tool name for existing OpenCode skills and prompts.

Core parameters:

- `file_path`
- `output_format`

### `convert_pdf`

Upstream-aligned alias.

Core parameters:

- `input_path`
- `format`

### Supported output formats

- `json`
- `text`
- `html`
- `markdown`
- `markdown-with-html`
- `markdown-with-images`

Additional upstream options are passed through, including `password`, `pages`, `sanitize`, `keep_line_breaks`, `detect_strikethrough`, image options, and hybrid options.

## Wrapper behavior

This server intentionally keeps a few local behaviors:

- 50MB file size cap
- local PDF validation before conversion
- `Error: ...` string returns instead of raised exceptions
- embedded images forced for `markdown-with-images` when `image_output` is omitted
- `quiet=True` during conversion

## Support scope

This project is intended to be publicly shareable, and the verified surface is now broader than a single local machine:

- verified locally with Python 3.11 on Windows
- CI is configured for Windows, macOS, and Linux across Python 3.10, 3.11, and 3.12
- packaged successfully as both wheel and sdist
- tested through direct function calls and MCP stdio handshake
- aligned with upstream `opendataloader-pdf` `v2.2.0`

Known limits:

- scanned/image PDFs can still return empty or low-quality text
- Java 11+ must be installed by the user
- wrapper-specific 50MB size limit remains in place
- broader PDF-type coverage still depends on real-world testing beyond the included fixture set

## OpenCode configuration

After `pip install -e .` or a normal package install, OpenCode can launch the installed command directly:

```json
{
  "mcp": {
    "opendataloader-pdf": {
      "command": ["opendataloader-pdf-mcp"],
      "enabled": true,
      "type": "local"
    }
  }
}
```

## OpenCode skill file

The repository includes an OpenCode skill at `skills/opendataloader-pdf/SKILL.md`.
If you want the same automatic tool guidance, copy that folder into your OpenCode skills directory.

## Migration and compatibility

This release renamed the project from `pdf-analyzer-mcp` / `pdf_analyzer` to `opendataloader-pdf-mcp` / `opendataloader_pdf_mcp`.

Temporary compatibility shims are still included for **one transition cycle** and are planned for removal in **v0.2.0**:

- old CLI alias: `pdf-analyzer-mcp`
- old import path: `pdf_analyzer`
- root-level local shims: `server.py` and `test_server.py`

Recommended migration now:

- CLI: `pdf-analyzer-mcp` → `opendataloader-pdf-mcp`
- Python: `python -m pdf_analyzer` → `python -m opendataloader_pdf_mcp`
- imports: `from pdf_analyzer ...` → `from opendataloader_pdf_mcp ...`
- OpenCode config key: `pdf-analyzer` → `opendataloader-pdf`
- OpenCode skill folder: `skills/pdf-analyzer` → `skills/opendataloader-pdf`

## Before publishing to PyPI or announcing widely

Project URLs are already set for the intended public repository:

- `https://github.com/bokjk/opendataloader-pdf-mcp`
- `https://github.com/bokjk/opendataloader-pdf-mcp/issues`

If you decide to publish under a different repository, update `[project.urls]` in `pyproject.toml` before uploading to PyPI.

## Local development compatibility

The repository still keeps root-level `server.py` and `test_server.py` shims, and it temporarily ships a `pdf-analyzer-mcp` CLI alias plus a `pdf_analyzer` import shim for compatibility during the v0.1.x transition period.

## Tests

```bash
python test_server.py
```

## Build distributions

```bash
python -m build
```

## Publish later

When you are ready to publish publicly, the repo already includes the package layout, entry point, license, and build metadata. At that point you only need to choose your repository URL and upload destination.
