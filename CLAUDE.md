# Claude Configuration for query_radiant_vds

This project follows [ownjoo-org](https://github.com/ownjoo-org) standards and guidelines.

## Key Standards

- **Simplicity First** — Write the simplest code that solves the problem. No premature optimization.
- **Integration Testing** — Prefer integration tests hitting real dependencies over mocks.
- **No Defensive Code** — Only validate at system boundaries (CLI input, API responses). Trust internal code.
- **Security by Default** — Never introduce command injection, XSS, SQL injection, or OWASP Top 10 vulnerabilities.
- **Explicit Commits** — Use conventional commits with clear messages and `Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>`.

## Code Quality

- **Type Hints** — All functions have type annotations. Run `mypy` to validate.
- **Linting** — Use `ruff` for linting and `black` for formatting.
- **Testing** — Use `pytest` and `pytest-asyncio` for async tests.
- **Coverage** — Aim for >80% coverage on new code.

## Development Workflow

1. Create feature branch from `main`
2. Make focused commits following conventional commit format
3. Run quality checks: `make lint format type-check test`
4. Submit PR with clear description and testing approach
5. All CI checks must pass before merge

## Key Files

- **`CLAUDE.md`** — This file (organization standards)
- **`pyproject.toml`** — Project metadata, dependencies, tool configuration
- **`Makefile`** — Common development commands
- **`.github/workflows/ci.yml`** — Automated CI/CD pipeline

## Async Patterns

This project demonstrates async HTTP patterns using:

- **`httpx`** — Modern async HTTP client with HTTP/2 support
- **`asyncio.Queue`** — Coordinates concurrent tasks (producers/consumers)
- **`retry-async`** — Automatic retry with exponential backoff
- **`pytest-asyncio`** — Async test support

See `query_radiant_vds/client.py` and `query_radiant_vds/main.py` for examples.

## Contributing

Before making changes:

1. Read this file (CLAUDE.md)
2. Review the full [ownjoo-org CLAUDE.md](https://github.com/ownjoo-org/claude/blob/main/CLAUDE.md)
3. Follow the patterns in this project
4. Update this file if new standards should be documented

Questions? See [ownjoo-org/claude](https://github.com/ownjoo-org/claude) for detailed guidelines.
