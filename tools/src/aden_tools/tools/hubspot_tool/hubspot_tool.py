"""
HubSpot Tool - Search, get, create, and update HubSpot CRM objects.

Supports:
- Contacts: Search, get, create, update
- Companies: Search, get, create, update
- Deals: Search, get, create, update

Authentication:
- OAuth2 (recommended for production)
- API Key (HUBSPOT_API_KEY environment variable)
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Literal

import httpx
from fastmcp import FastMCP

if TYPE_CHECKING:
    from aden_tools.credentials import CredentialManager


# HubSpot API base URL
HUBSPOT_API_BASE = "https://api.hubapi.com"

# Object type mapping
ObjectType = Literal["contacts", "companies", "deals"]


def register_tools(
    mcp: FastMCP,
    credentials: CredentialManager | None = None,
) -> None:
    """Register HubSpot tools with the MCP server."""

    def _get_auth_headers() -> dict[str, str]:
        """Get authentication headers for HubSpot API."""
        # Try OAuth2 token from credential manager first
        if credentials:
            token = credentials.get("hubspot_oauth_token")
            if token:
                return {"Authorization": f"Bearer {token}"}

        # Fall back to API key from environment
        api_key = os.getenv("HUBSPOT_API_KEY")
        if api_key:
            return {"Authorization": f"Bearer {api_key}"}

        raise ValueError("HubSpot credentials not found. Set HUBSPOT_API_KEY or configure OAuth2.")

    def _make_request(
        method: str,
        endpoint: str,
        json_data: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        """Make authenticated request to HubSpot API."""
        headers = _get_auth_headers()
        headers["Content-Type"] = "application/json"

        url = f"{HUBSPOT_API_BASE}{endpoint}"

        response = httpx.request(
            method=method,
            url=url,
            headers=headers,
            json=json_data,
            params=params,
            timeout=30.0,
        )

        if response.status_code == 401:
            return {"error": "Invalid or expired HubSpot credentials"}
        elif response.status_code == 403:
            return {"error": "Access forbidden. Check API permissions."}
        elif response.status_code == 429:
            return {"error": "Rate limit exceeded. Try again later."}
        elif response.status_code >= 400:
            return {"error": f"HubSpot API error: HTTP {response.status_code}"}

        return response.json()

    # === SEARCH TOOLS ===

    @mcp.tool()
    def hubspot_search(
        object_type: ObjectType,
        query: str,
        properties: list[str] | None = None,
        limit: int = 10,
    ) -> dict:
        """
        Search HubSpot CRM objects (contacts, companies, or deals).

        Args:
            object_type: Type of object to search ("contacts", "companies", "deals")
            query: Search query string
            properties: List of properties to return (default: basic properties)
            limit: Maximum number of results (1-100, default: 10)

        Returns:
            Search results with matching objects
        """
        if limit < 1 or limit > 100:
            return {"error": "limit must be between 1 and 100"}

        # Default properties per object type
        default_properties = {
            "contacts": ["firstname", "lastname", "email", "phone", "company"],
            "companies": ["name", "domain", "industry", "city", "state"],
            "deals": ["dealname", "amount", "dealstage", "closedate", "pipeline"],
        }

        props = properties or default_properties.get(object_type, [])

        search_body = {
            "query": query,
            "limit": limit,
            "properties": props,
        }

        result = _make_request(
            "POST",
            f"/crm/v3/objects/{object_type}/search",
            json_data=search_body,
        )

        if "error" in result:
            return result

        return {
            "object_type": object_type,
            "query": query,
            "total": result.get("total", 0),
            "results": result.get("results", []),
        }

    # === GET TOOLS ===

    @mcp.tool()
    def hubspot_get(
        object_type: ObjectType,
        object_id: str,
        properties: list[str] | None = None,
    ) -> dict:
        """
        Get a single HubSpot CRM object by ID.

        Args:
            object_type: Type of object ("contacts", "companies", "deals")
            object_id: The HubSpot object ID
            properties: List of properties to return (optional)

        Returns:
            The requested object with its properties
        """
        params = {}
        if properties:
            params["properties"] = ",".join(properties)

        result = _make_request(
            "GET",
            f"/crm/v3/objects/{object_type}/{object_id}",
            params=params if params else None,
        )

        return result

    # === CREATE TOOLS ===

    @mcp.tool()
    def hubspot_create(
        object_type: ObjectType,
        properties: dict,
    ) -> dict:
        """
        Create a new HubSpot CRM object.

        Args:
            object_type: Type of object to create ("contacts", "companies", "deals")
            properties: Object properties as key-value pairs
                - For contacts: firstname, lastname, email, phone, etc.
                - For companies: name, domain, industry, etc.
                - For deals: dealname, amount, dealstage, pipeline, etc.

        Returns:
            The created object with its ID
        """
        if not properties:
            return {"error": "properties cannot be empty"}

        create_body = {"properties": properties}

        result = _make_request(
            "POST",
            f"/crm/v3/objects/{object_type}",
            json_data=create_body,
        )

        return result

    # === UPDATE TOOLS ===

    @mcp.tool()
    def hubspot_update(
        object_type: ObjectType,
        object_id: str,
        properties: dict,
    ) -> dict:
        """
        Update an existing HubSpot CRM object.

        Args:
            object_type: Type of object ("contacts", "companies", "deals")
            object_id: The HubSpot object ID to update
            properties: Properties to update as key-value pairs

        Returns:
            The updated object
        """
        if not properties:
            return {"error": "properties cannot be empty"}

        update_body = {"properties": properties}

        result = _make_request(
            "PATCH",
            f"/crm/v3/objects/{object_type}/{object_id}",
            json_data=update_body,
        )

        return result

    # === ASSOCIATION TOOLS ===

    @mcp.tool()
    def hubspot_get_associations(
        from_object_type: ObjectType,
        from_object_id: str,
        to_object_type: ObjectType,
    ) -> dict:
        """
        Get associations between HubSpot objects.

        Args:
            from_object_type: Source object type
            from_object_id: Source object ID
            to_object_type: Target object type to find associations

        Returns:
            List of associated object IDs
        """
        result = _make_request(
            "GET",
            f"/crm/v3/objects/{from_object_type}/{from_object_id}/associations/{to_object_type}",
        )

        return result
