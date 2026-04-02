# query_radiant_vds

A Python CLI application for querying Radiant Logic IDM v8.1 via the ADAP (REST) endpoint. Demonstrates async HTTP patterns with `httpx`, `asyncio`, and `ownjoo-org/utils`.

## Features

- **Async HTTP Client** — Uses `httpx` with HTTP/2 support for ADAP queries
- **Automatic Retries** — Built-in retry logic with exponential backoff via `retry-async`
- **Queue-Based Coordination** — Coordinates ADAP search and JSON output using `asyncio.Queue`
- **Basic Authentication** — HTTP Basic Auth with base64-encoded credentials
- **Structured Logging** — Integration with `ownjoo-org/utils` logging utilities
- **Type-Safe** — Full type hints with mypy validation
- **Comprehensive Testing** — Unit and integration tests with pytest

## Setup

### Prerequisites

- Python 3.10+
- pip
- Radiant Logic IDM v8.1 instance with ADAP endpoint enabled

### Installation

```bash
# Clone the repository
git clone https://github.com/ownjoo-org/query_radiant_vds.git
cd query_radiant_vds

# Install development dependencies
pip install -e ".[dev]"
```

## Usage

### Basic Command

```bash
python main.py \
  --username <username> \
  --password <password> \
  --domain <radiant-fqdn> \
  --port <adap-port> \
  --search-filter "<ldap-filter>"
```

### Options

```
$ python main.py --help
usage: main.py [-h] --username USERNAME --password PASSWORD --domain DOMAIN
                [--port PORT] --search-filter SEARCH_FILTER [--proxies PROXIES]
                [--log-level LOG_LEVEL]

options:
  -h, --help                     show this help message and exit
  --username USERNAME            Username for authentication (required)
  --password PASSWORD            Password for authentication (required)
  --domain DOMAIN                RadiantOne server FQDN or IP address (required)
  --port PORT                    ADAP endpoint port (default: 8080)
  --search-filter SEARCH_FILTER  LDAP search filter, e.g. "(cn=*)" (required)
  --proxies PROXIES              JSON structure specifying 'http' and 'https' proxy URLs
  --log-level LOG_LEVEL          Logging level 0 (NOTSET) - 50 (CRITICAL) (default: 20)
```

### Examples

```bash
# Search for all entries
python main.py \
  --username admin \
  --password secret \
  --domain radiant.example.com \
  --port 8080 \
  --search-filter "(objectClass=*)"

# Search for users by cn
python main.py \
  --username admin \
  --password secret \
  --domain radiant.example.com \
  --port 8080 \
  --search-filter "(cn=john*)"

# Search with custom port and proxy
python main.py \
  --username admin \
  --password secret \
  --domain radiant.example.com \
  --port 9443 \
  --search-filter "(mail=*@example.com)" \
  --proxies '{"http": "http://proxy:8080", "https": "https://proxy:8080"}'

# With debug logging
python main.py \
  --username admin \
  --password secret \
  --domain radiant.example.com \
  --port 8080 \
  --search-filter "(uid=*)" \
  --log-level 10
```

## Development

### Make Commands

```bash
make install          # Install production dependencies
make install-dev      # Install development dependencies
make lint             # Run linting checks
make format           # Format code with black
make type-check       # Run type checking with mypy
make test             # Run tests
make test-cov         # Run tests with coverage report
make clean            # Remove build artifacts and caches
make run              # Show CLI help
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=query_radiant_vds

# Run specific test file
pytest test/unit/test_client.py -v
```

### Code Quality

The project uses:

- **black** for code formatting
- **ruff** for linting
- **mypy** for type checking
- **pytest** for testing
- **pytest-asyncio** for async test support

All checks run automatically in the CI/CD pipeline (GitHub Actions).

## Architecture

### Module Structure

```
query_radiant_vds/
├── __init__.py          # Package initialization
├── __main__.py          # Module entry point
├── main.py              # Async orchestration (Queue, gather)
├── client.py            # Async HTTP client with httpx (ADAP queries)
├── parser.py            # Output formatter (JSON)
├── tracker.py           # Task coordination
└── consts.py            # Constants (retry config)
```

### Key Patterns

#### Async Client (`client.py`)

- `get_response()` — Async HTTP request with retry logic
- `list_results_paginated()` — Async generator for paginated endpoints
- `list_characters/locations/episodes()` — Concurrent endpoint fetchers

#### Queue Coordination

```python
q = Queue(maxsize=100)
await gather(
    list_characters(url=domain, q=q),
    list_locations(url=domain, q=q),
    list_episodes(url=domain, q=q),
    json_out(q=q),
    q.join(),
)
```

#### Basic Authentication

Credentials are sent as HTTP Basic Auth header:

```python
credentials = base64.b64encode(f'{username}:{password}'.encode()).decode()
session.headers.update({'Authorization': f'Basic {credentials}'})
```

## Contributing

See [CLAUDE.md](CLAUDE.md) for organization standards and best practices.

## Standards

This project adheres to [ownjoo-org](https://github.com/ownjoo-org) standards:

- **Simplicity First** — Write the simplest code that solves the problem
- **Integration Testing** — Prefer real dependencies over mocks
- **Security by Default** — No OWASP Top 10 vulnerabilities
- **Explicit Commits** — Use conventional commits with clear history

See the [claude configuration hub](https://github.com/ownjoo-org/claude) for full guidelines.

## License

MIT
