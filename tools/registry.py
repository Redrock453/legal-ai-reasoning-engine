"""Tool registry for open-code runtime."""

from legal_tool import legal_tool
from repo_tool import repo_tool


TOOLS = {
    "legal": legal_tool,
    "repo": repo_tool
}


def get_tool(name: str):
    """Get tool by name."""
    return TOOLS.get(name)


def list_tools():
    """List available tools."""
    return list(TOOLS.keys())


if __name__ == "__main__":
    print("Available tools:", list_tools())