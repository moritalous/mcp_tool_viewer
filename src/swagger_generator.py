"""Swagger UI HTML generator using FastAPI docs.py pattern."""

import json
from typing import Any, Dict


class SwaggerGenerator:
    """Generate Swagger UI HTML from OpenAPI specification."""

    @staticmethod
    def generate_swagger_html(
        openapi_spec: Dict[str, Any], title: str = "MCP Tools Documentation"
    ) -> str:
        """Generate Swagger UI HTML with embedded OpenAPI specification."""
        return SwaggerGenerator.create_html_template(openapi_spec, title)

    @staticmethod
    def create_html_template(openapi_spec: Dict[str, Any], title: str) -> str:
        """Create HTML template with embedded OpenAPI JSON for Swagger UI."""
        openapi_json = json.dumps(openapi_spec, indent=2)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" />
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        *, *:before, *:after {{
            box-sizing: inherit;
        }}
        body {{
            margin:0;
            background: #fafafa;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const spec = {openapi_json};
            
            const ui = SwaggerUIBundle({{
                spec: spec,
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            }});
        }};
    </script>
</body>
</html>"""

        return html
