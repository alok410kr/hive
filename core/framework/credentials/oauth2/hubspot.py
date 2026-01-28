"""
HubSpot OAuth2 Provider.

Implements OAuth2 authentication for HubSpot CRM API.

HubSpot OAuth2 endpoints:
- Authorization: https://app.hubspot.com/oauth/authorize
- Token: https://api.hubapi.com/oauth/v1/token
- Token Info: https://api.hubapi.com/oauth/v1/access-tokens/{token}

Scopes documentation: https://developers.hubspot.com/docs/api/oauth-quickstart-guide
"""

from __future__ import annotations

from .base_provider import BaseOAuth2Provider
from .provider import OAuth2Config


class HubSpotOAuth2Provider(BaseOAuth2Provider):
    """
    OAuth2 provider for HubSpot CRM.

    Supports:
    - Authorization Code flow (for user-authorized access)
    - Refresh Token flow (for token renewal)

    Note: HubSpot does NOT support Client Credentials flow.
    All access requires user authorization.

    Example:
        provider = HubSpotOAuth2Provider(
            client_id="your-client-id",
            client_secret="your-client-secret",
            redirect_uri="https://your-app.com/oauth/callback",
        )

        # Generate authorization URL
        auth_url = provider.get_authorization_url(
            state="random-state-string",
            redirect_uri="https://your-app.com/oauth/callback",
            scopes=["crm.objects.contacts.read", "crm.objects.contacts.write"],
        )

        # After user authorizes, exchange code for token
        token = provider.exchange_code(
            code="authorization-code-from-callback",
            redirect_uri="https://your-app.com/oauth/callback",
        )

        # Refresh token when expired
        new_token = provider.refresh_token(token.refresh_token)
    """

    # HubSpot OAuth2 endpoints
    AUTHORIZATION_URL = "https://app.hubspot.com/oauth/authorize"
    TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"

    # Common HubSpot scopes
    SCOPES = {
        # Contacts
        "contacts_read": "crm.objects.contacts.read",
        "contacts_write": "crm.objects.contacts.write",
        # Companies
        "companies_read": "crm.objects.companies.read",
        "companies_write": "crm.objects.companies.write",
        # Deals
        "deals_read": "crm.objects.deals.read",
        "deals_write": "crm.objects.deals.write",
        # Tickets
        "tickets_read": "crm.objects.tickets.read",
        "tickets_write": "crm.objects.tickets.write",
        # Line Items
        "line_items_read": "crm.objects.line_items.read",
        "line_items_write": "crm.objects.line_items.write",
        # Quotes
        "quotes_read": "crm.objects.quotes.read",
        "quotes_write": "crm.objects.quotes.write",
        # Owners
        "owners_read": "crm.objects.owners.read",
    }

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str | None = None,
        scopes: list[str] | None = None,
    ):
        """
        Initialize HubSpot OAuth2 provider.

        Args:
            client_id: HubSpot OAuth2 app client ID
            client_secret: HubSpot OAuth2 app client secret
            redirect_uri: OAuth2 callback URL (required for authorization flow)
            scopes: List of HubSpot scopes to request
                    Default: contacts and companies read/write
        """
        default_scopes = [
            self.SCOPES["contacts_read"],
            self.SCOPES["contacts_write"],
            self.SCOPES["companies_read"],
            self.SCOPES["companies_write"],
            self.SCOPES["deals_read"],
            self.SCOPES["deals_write"],
        ]

        config = OAuth2Config(
            token_url=self.TOKEN_URL,
            authorization_url=self.AUTHORIZATION_URL,
            client_id=client_id,
            client_secret=client_secret,
            default_scopes=scopes or default_scopes,
        )

        super().__init__(config, provider_id="hubspot")
        self._redirect_uri = redirect_uri

    def get_authorization_url(
        self,
        state: str,
        redirect_uri: str | None = None,
        scopes: list[str] | None = None,
        **kwargs,
    ) -> str:
        """
        Generate HubSpot authorization URL.

        Args:
            state: Anti-CSRF state parameter
            redirect_uri: OAuth2 callback URL (overrides default)
            scopes: Scopes to request (overrides default)
            **kwargs: Additional query parameters

        Returns:
            Authorization URL to redirect user
        """
        uri = redirect_uri or self._redirect_uri
        if not uri:
            raise ValueError("redirect_uri is required for HubSpot authorization")

        return super().get_authorization_url(
            state=state,
            redirect_uri=uri,
            scopes=scopes,
            **kwargs,
        )

    def exchange_code(
        self,
        code: str,
        redirect_uri: str | None = None,
        **kwargs,
    ):
        """
        Exchange authorization code for tokens.

        Args:
            code: Authorization code from callback
            redirect_uri: Same redirect_uri used in authorization (overrides default)
            **kwargs: Additional parameters

        Returns:
            OAuth2Token with access_token and refresh_token
        """
        uri = redirect_uri or self._redirect_uri
        if not uri:
            raise ValueError("redirect_uri is required for token exchange")

        return super().exchange_code(code=code, redirect_uri=uri, **kwargs)

    def get_token_info(self, access_token: str) -> dict:
        """
        Get information about an access token.

        Args:
            access_token: The access token to inspect

        Returns:
            Token metadata including user, hub_id, scopes, expires_in
        """
        client = self._get_client()

        response = client.get(
            f"https://api.hubapi.com/oauth/v1/access-tokens/{access_token}",
            timeout=self.config.request_timeout,
        )

        if response.status_code != 200:
            raise ValueError(f"Failed to get token info: {response.status_code}")

        return response.json()
