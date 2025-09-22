"""OpenAPI converter for MCP tools."""

from typing import Any, Dict, List


class OpenAPIConverter:
    """Convert MCP tools to OpenAPI 3.0.3 specification."""

    @staticmethod
    def convert_tools_to_openapi(
        tools: List[Dict[str, Any]], server_name: str = "MCP Server"
    ) -> Dict[str, Any]:
        """Convert MCP tools to OpenAPI specification."""
        openapi_spec = OpenAPIConverter.create_openapi_spec(server_name, tools)

        # Add paths for each tool
        for tool in tools:
            path_item = OpenAPIConverter.tool_to_path_item(tool)
            openapi_spec["paths"][f"/{tool['name']}"] = path_item

        return openapi_spec

    @staticmethod
    def create_openapi_spec(
        server_name: str, tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create base OpenAPI specification structure."""
        return {
            "openapi": "3.0.3",
            "info": {
                "title": f"{server_name} Tools",
                "description": f"API documentation for {server_name} MCP tools",
                "version": "1.0.0",
            },
            "servers": [{"url": "http://localhost:8000", "description": "MCP Server"}],
            "paths": {},
            "components": {"schemas": {}},
        }

    @staticmethod
    def tool_to_path_item(tool: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a single MCP tool to OpenAPI path item."""
        tool_name = tool["name"]
        description = tool["description"]
        input_schema = tool.get("inputSchema", {})

        # Create request body schema
        request_schema = {
            "type": "object",
            "properties": input_schema.get("properties", {}),
            "required": input_schema.get("required", []),
        }

        return {
            "post": {
                "summary": tool_name,
                "description": description,
                "operationId": tool_name,
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": request_schema}},
                },
                "responses": {
                    "200": {
                        "description": "Tool execution result",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "result": {
                                            "type": "string",
                                            "description": "Tool execution result",
                                        }
                                    },
                                }
                            }
                        },
                    }
                },
            }
        }
