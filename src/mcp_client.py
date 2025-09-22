"""MCP Client for connecting to MCP servers via stdio and Streamable HTTP transports."""

from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client


class MCPClient:
    """Client for connecting to MCP servers via stdio or Streamable HTTP transport."""

    @staticmethod
    async def connect_stdio(
        command: str, args: List[str], env: Dict[str, str]
    ) -> ClientSession:
        """Connect to MCP server via stdio transport."""
        server_params = StdioServerParameters(command=command, args=args, env=env)

        # Create connection
        read, write = await stdio_client(server_params).__aenter__()
        session = ClientSession(read, write)
        await session.__aenter__()

        # Initialize connection
        await session.initialize()

        return session

    @staticmethod
    async def connect_http(url: str) -> ClientSession:
        """Connect to MCP server via Streamable HTTP transport."""
        # Create connection
        read, write, _ = await streamablehttp_client(url).__aenter__()
        session = ClientSession(read, write)
        await session.__aenter__()

        # Initialize connection
        await session.initialize()

        return session

    @staticmethod
    async def get_tools(session: ClientSession) -> List[Any]:
        """Get tools from MCP server session."""
        try:
            tools_response = await session.list_tools()
            return tools_response.tools
        except Exception as e:
            raise RuntimeError(f"Failed to get tools: {e}")

    @staticmethod
    def normalize_tool_info(tools: List[Any]) -> List[Dict[str, Any]]:
        """Normalize tool information to dictionary format."""
        normalized_tools = []

        for tool in tools:
            tool_info = {
                "name": tool.name,
                "description": tool.description or "",
                "inputSchema": tool.inputSchema or {},
            }
            normalized_tools.append(tool_info)

        return normalized_tools

    @staticmethod
    async def get_normalized_tools(
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        url: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Connect to MCP server and get normalized tool information.

        Args:
            command: Command for stdio transport
            args: Arguments for stdio transport
            env: Environment variables for stdio transport
            url: URL for Streamable HTTP transport

        Returns:
            List of normalized tool information
        """
        if url:
            # Streamable HTTP transport
            try:
                async with streamablehttp_client(url) as (read, write, _):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        tools_response = await session.list_tools()
                        return MCPClient.normalize_tool_info(tools_response.tools)
            except Exception as e:
                raise RuntimeError(f"MCP HTTP connection failed: {e}")

        elif command and args is not None and env is not None:
            # stdio transport
            server_params = StdioServerParameters(command=command, args=args, env=env)

            try:
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        tools_response = await session.list_tools()
                        return MCPClient.normalize_tool_info(tools_response.tools)
            except Exception as e:
                raise RuntimeError(f"MCP stdio connection failed: {e}")

        else:
            raise ValueError(
                "Either 'url' for HTTP or 'command/args/env' for stdio must be provided"
            )
