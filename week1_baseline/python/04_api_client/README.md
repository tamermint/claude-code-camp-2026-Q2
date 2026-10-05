# The API Client

The API Client takes the payload assembled by `PromptBuilder` and sends it to the API. One HTTP POST, one response. No tool loop yet — just proving the round trip works.

## New Files

| File | Description |
|---|---|
| `boukensha/client.py` | Stateless HTTP client that makes the request, handles retries, and parses the response |
| `boukensha/errors.py` | Defines `ApiError` alongside Boukensha exceptions |

## How It Works

```
Context (Python objects)
      ↓
PromptBuilder
      ↓
Client (Stateless HTTP Transport)
      ↓
POST to API endpoint
      ↓
Raw JSON response
```

## Boukensha::Client (Python: `Client`)

| Method | Description |
|---|---|
| `Client(max_retries=3, base_retry_delay=0.5)` | Initializes stateless transport client with retry policies |
| `call(builder, max_output_tokens=1024)` | POSTs the builder's payload to its URL with exponential backoff and returns the parsed JSON response |

## Stateless Architecture

The client does **not** store `PromptBuilder` in `__init__`. Instead, `PromptBuilder` is passed into `client.call(builder)`. 
This allows a single `Client` instance to be initialized once and reused across turns in the agent loop without state leakage.

## No External SDK Dependencies

`Client` uses Python's standard library `urllib.request`, `ssl`, and `json`. No external HTTP libraries or vendor SDKs are required.

## Run Example

```sh
./bin/python/04_api_client.sh
```
