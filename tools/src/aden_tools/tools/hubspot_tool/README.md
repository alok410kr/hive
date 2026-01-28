# HubSpot Tool

CRM operations for HubSpot contacts, companies, and deals.

## Features

- **Search**: Find contacts, companies, or deals by query
- **Get**: Retrieve a single object by ID
- **Create**: Create new contacts, companies, or deals
- **Update**: Update existing objects
- **Associations**: Get relationships between objects

## Authentication

### Option 1: API Key (Simple)

Set the `HUBSPOT_API_KEY` environment variable:

```bash
export HUBSPOT_API_KEY="your-hubspot-api-key"
```

### Option 2: OAuth2 (Recommended for Production)

Use the HubSpot OAuth2 provider with the credential store:

```python
from framework.credentials import CredentialStore
from framework.credentials.oauth2 import HubSpotOAuth2Provider

store = CredentialStore()
provider = HubSpotOAuth2Provider(
    client_id="your-client-id",
    client_secret="your-client-secret",
)
store.register_provider(provider)
```

## Usage

### Search Contacts

```python
result = hubspot_search(
    object_type="contacts",
    query="john@example.com",
    limit=10,
)
```

### Get a Company

```python
company = hubspot_get(
    object_type="companies",
    object_id="123456",
    properties=["name", "domain", "industry"],
)
```

### Create a Contact

```python
contact = hubspot_create(
    object_type="contacts",
    properties={
        "firstname": "John",
        "lastname": "Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
    },
)
```

### Update a Deal

```python
deal = hubspot_update(
    object_type="deals",
    object_id="789",
    properties={
        "amount": "50000",
        "dealstage": "closedwon",
    },
)
```

## HubSpot API Scopes

For OAuth2, request these scopes based on your needs:

| Scope | Access |
|-------|--------|
| `crm.objects.contacts.read` | Read contacts |
| `crm.objects.contacts.write` | Create/update contacts |
| `crm.objects.companies.read` | Read companies |
| `crm.objects.companies.write` | Create/update companies |
| `crm.objects.deals.read` | Read deals |
| `crm.objects.deals.write` | Create/update deals |

## Rate Limits

HubSpot has rate limits based on your subscription:

- **Free/Starter**: 100 requests per 10 seconds
- **Professional/Enterprise**: 150 requests per 10 seconds

The tool returns a rate limit error if exceeded.
