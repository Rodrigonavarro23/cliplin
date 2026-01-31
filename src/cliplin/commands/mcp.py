"""MCP server command. Runs the Storage MCP with stdio transport (for Cursor/Claude)."""

import typer

from cliplin.mcp_server import run_mcp_server


def mcp_command() -> None:
    """Run the Cliplin Storage MCP server. Used by Cursor/Claude via mcp.json; do not print to stdout."""
    run_mcp_server()
