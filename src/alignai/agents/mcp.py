"""Optional MCP servers (filesystem + fetch); degrades to no MCP when unavailable."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path


@asynccontextmanager
async def optional_mcp_servers(_data_root: Path) -> AsyncIterator[list[object]]:
    """Yield MCP servers for ``MCPServerManager``; empty when Node/npx is unavailable.

    Intended registrations (when tooling is present):

    * Filesystem MCP — ``@modelcontextprotocol/server-filesystem`` scoped to the
      AlignAI data directory.
    * Fetch MCP — ``mcp-server-fetch`` for plain HTTP retrieval.

    The desktop MVP runs without MCP by yielding ``[]``; built-in httpx + Playwright
    fetchers cover the same workflows.
    """
    # Wiring concrete stdio servers requires Node.js on PATH; enable per deployment.
    yield []
