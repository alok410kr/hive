"""
HubSpot Tool - CRM operations for contacts, companies, and deals.

Supports OAuth2 authentication via HubSpot's API.
"""

from .hubspot_tool import register_tools

__all__ = ["register_tools"]
