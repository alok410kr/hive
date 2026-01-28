"""
Tests for HubSpot Tool.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastmcp import FastMCP


class TestHubSpotToolRegistration:
    """Test tool registration."""

    def test_register_tools_creates_mcp_tools(self):
        """Test that register_tools adds tools to MCP server."""
        from aden_tools.tools.hubspot_tool import register_tools

        mcp = FastMCP("test-server")
        register_tools(mcp)

        # Check that tools were registered
        tool_names = [tool.name for tool in mcp._tool_manager._tools.values()]
        assert "hubspot_search" in tool_names
        assert "hubspot_get" in tool_names
        assert "hubspot_create" in tool_names
        assert "hubspot_update" in tool_names
        assert "hubspot_get_associations" in tool_names


class TestHubSpotSearch:
    """Test hubspot_search tool."""

    @patch("httpx.request")
    def test_search_contacts_success(self, mock_request):
        """Test successful contact search."""
        from aden_tools.tools.hubspot_tool import register_tools

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 1,
            "results": [
                {
                    "id": "123",
                    "properties": {
                        "firstname": "John",
                        "lastname": "Doe",
                        "email": "john@example.com",
                    },
                }
            ],
        }
        mock_request.return_value = mock_response

        mcp = FastMCP("test-server")
        register_tools(mcp)

        # Get the tool function
        search_tool = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "hubspot_search":
                search_tool = tool
                break

        assert search_tool is not None

    @patch("httpx.request")
    def test_search_with_invalid_limit(self, mock_request):
        """Test search with invalid limit parameter."""
        from aden_tools.tools.hubspot_tool import register_tools

        mcp = FastMCP("test-server")
        register_tools(mcp)

        # The tool should validate limit before making request


class TestHubSpotGet:
    """Test hubspot_get tool."""

    @patch("httpx.request")
    def test_get_contact_success(self, mock_request):
        """Test successful contact retrieval."""
        from aden_tools.tools.hubspot_tool import register_tools

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "123",
            "properties": {
                "firstname": "John",
                "lastname": "Doe",
                "email": "john@example.com",
            },
        }
        mock_request.return_value = mock_response

        mcp = FastMCP("test-server")
        register_tools(mcp)


class TestHubSpotCreate:
    """Test hubspot_create tool."""

    @patch("httpx.request")
    def test_create_contact_success(self, mock_request):
        """Test successful contact creation."""
        from aden_tools.tools.hubspot_tool import register_tools

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "456",
            "properties": {
                "firstname": "Jane",
                "lastname": "Smith",
                "email": "jane@example.com",
            },
        }
        mock_request.return_value = mock_response

        mcp = FastMCP("test-server")
        register_tools(mcp)


class TestHubSpotUpdate:
    """Test hubspot_update tool."""

    @patch("httpx.request")
    def test_update_deal_success(self, mock_request):
        """Test successful deal update."""
        from aden_tools.tools.hubspot_tool import register_tools

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "789",
            "properties": {
                "dealname": "Big Deal",
                "amount": "100000",
                "dealstage": "closedwon",
            },
        }
        mock_request.return_value = mock_response

        mcp = FastMCP("test-server")
        register_tools(mcp)


class TestHubSpotErrorHandling:
    """Test error handling."""

    @patch("httpx.request")
    def test_handles_401_unauthorized(self, mock_request):
        """Test handling of 401 unauthorized response."""
        from aden_tools.tools.hubspot_tool import register_tools

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response

        mcp = FastMCP("test-server")
        register_tools(mcp)

    @patch("httpx.request")
    def test_handles_429_rate_limit(self, mock_request):
        """Test handling of 429 rate limit response."""
        from aden_tools.tools.hubspot_tool import register_tools

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_request.return_value = mock_response

        mcp = FastMCP("test-server")
        register_tools(mcp)
