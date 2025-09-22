"""MCP Tool Viewer - Streamlit application for viewing MCP server tools as Redoc documentation."""

import asyncio
import json

import streamlit as st
import streamlit.components.v1 as components

from src.mcp_client import MCPClient
from src.openapi_converter import OpenAPIConverter
from src.swagger_generator import SwaggerGenerator

# Default MCP server configuration
default_mcp_server = {
    "awslabs.aws-documentation-mcp-server": {
        "command": "uvx",
        "args": ["awslabs.aws-documentation-mcp-server@latest"],
        "env": {"FASTMCP_LOG_LEVEL": "ERROR", "AWS_DOCUMENTATION_PARTITION": "aws"},
    }
}

# Streamlit page configuration
st.set_page_config(
    page_title="MCP Tool Viewer",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar for MCP server configuration
with st.sidebar:
    st.title("🔧 MCP Tool Viewer")

    st.header("MCP Server Configuration")
    mcp_config_text = st.text_area(
        "MCP Server Config (JSON)",
        value=json.dumps(default_mcp_server, indent=2, ensure_ascii=False),
        height="content",
        help="Configure your MCP server connection parameters",
    )

    convert_button = st.button(
        "🔄 Generate Documentation", type="primary", width="stretch"
    )

# Main content area
if convert_button:
    try:
        # Parse MCP configuration
        with st.sidebar:
            with st.spinner("Parsing configuration..."):
                mcp_config = json.loads(mcp_config_text)

        if not mcp_config:
            st.sidebar.error("❌ Empty configuration provided")
            st.stop()

        # Get first server configuration
        server_name = list(mcp_config.keys())[0]
        server_config = mcp_config[server_name]

        # Extract connection parameters
        command = server_config.get("command")
        args = server_config.get("args", [])
        env = server_config.get("env", {})
        url = server_config.get("url")

        if not command and not url:
            st.sidebar.error(
                "❌ Missing 'command' (stdio) or 'url' (HTTP) in server configuration"
            )
            st.stop()

        # Determine transport type
        transport_type = "HTTP" if url else "stdio"

        # Connect to MCP server and get tools
        with st.sidebar:
            with st.spinner(f"Connecting to {server_name} ({transport_type})..."):

                @st.cache_data
                def get_mcp_tools(
                    cmd: str, args_str: str, env_str: str, url_param: str
                ) -> list:
                    """Cached function to get MCP tools."""
                    if url_param:
                        return asyncio.run(
                            MCPClient.get_normalized_tools(url=url_param)
                        )
                    else:
                        return asyncio.run(
                            MCPClient.get_normalized_tools(
                                command=cmd,
                                args=json.loads(args_str) if args_str else [],
                                env=json.loads(env_str) if env_str else {},
                            )
                        )

                tools = get_mcp_tools(
                    cmd=command or "",
                    args_str=json.dumps(args),
                    env_str=json.dumps(env),
                    url_param=url or "",
                )

            st.success(f"✅ Connected! Found {len(tools)} tools")

            # Display server info in sidebar
            st.markdown("**Server Information:**")
            st.markdown(f"- **Name**: {server_name}")
            st.markdown(f"- **Transport**: {transport_type}")
            st.markdown(f"- **Tools**: {len(tools)}")
            if url:
                st.markdown(f"- **URL**: `{url}`")
            else:
                st.markdown(f"- **Command**: `{command}`")

        # Convert to OpenAPI
        with st.sidebar:
            with st.spinner("Converting to OpenAPI..."):

                @st.cache_data
                def convert_to_openapi(tools_json: str, srv_name: str) -> dict:
                    """Cached function to convert tools to OpenAPI."""
                    return OpenAPIConverter.convert_tools_to_openapi(
                        json.loads(tools_json), srv_name
                    )

                openapi_spec = convert_to_openapi(
                    tools_json=json.dumps(tools), srv_name=server_name
                )

        # Generate Swagger UI HTML
        with st.sidebar:
            with st.spinner("Generating documentation..."):
                html_content = SwaggerGenerator.generate_swagger_html(
                    openapi_spec, f"{server_name} Tools"
                )

            st.success("✅ Documentation generated!")

        # Display Swagger UI documentation (Main area - maximized)
        components.html(html_content, height=800, scrolling=True)

    except json.JSONDecodeError as e:
        st.error(f"❌ Invalid JSON configuration: {e}")
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.exception(e)
