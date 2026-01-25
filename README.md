# Spanish Public Data MCP

[![CI](https://github.com/mjgmario/spanish-public-info-radar-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/mjgmario/spanish-public-info-radar-mcp/actions/workflows/ci.yml)
[![Integration Tests](https://github.com/mjgmario/spanish-public-info-radar-mcp/actions/workflows/integration.yml/badge.svg)](https://github.com/mjgmario/spanish-public-info-radar-mcp/actions/workflows/integration.yml)
[![Coverage](https://img.shields.io/badge/coverage-70%25-green)](https://github.com/mjgmario/spanish-public-info-radar-mcp)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

MCP server for querying Spanish government open data APIs.

## Overview

Spanish Public Data MCP provides LLM-friendly tools for querying Spanish government data on-the-fly:

- **BDNS** - National Grants Database (grants and subsidies)
- **BOE** - Official Gazette (consolidated legislation)
- **BORME** - Company Registry Gazette (company acts)
- **INE** - National Statistics Institute (official statistics)
- **datos.gob.es** - National Open Data Catalog (40,000+ datasets)

**Architecture:** On-the-fly queries to official APIs. No database required.

**Total:** 26 MCP tools | 211 tests | 53%+ coverage

## Installation

```bash
# Clone repository
git clone https://github.com/mjgmario/spanish-public-info-radar-mcp.git
cd spanish-public-data-mcp

# Install with uv (recommended)
uv sync

# For development
uv sync --extra dev
```

## Quick Start

### Option 1: Run directly (development/testing)

```bash
# Install dependencies
uv sync

# Run MCP server (HTTP/SSE mode)
uv run python -m public_radar

# Or on a specific port
uv run python -m public_radar --port 9000

# Or in stdio mode (for Claude Desktop)
uv run python -m public_radar --stdio
```

### Option 2: With Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Verify it works

```bash
# Health check (HTTP mode)
curl http://localhost:8080/health

# Should return: {"status":"healthy","service":"spanish-public-data-mcp"}
```

## Claude Desktop Integration

### Step 1: Locate your config file

The Claude Desktop configuration file is located at:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

### Step 2: Add the MCP server configuration

Open the config file and add the following:

```json
{
  "mcpServers": {
    "spanish-public-data": {
      "command": "uv",
      "args": ["run", "python", "-m", "public_radar", "--stdio"],
      "cwd": "C:\\Users\\YOUR_USER\\path\\to\\spanish-public-data-mcp"
    }
  }
}
```

**Note:** Replace `YOUR_USER` and the path with your actual installation path.

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop to load the new MCP server.

### Step 4: Verify the connection

Ask Claude: "What Spanish public data tools do you have available?"

Claude should respond with information about the 26 available tools.

---

## Available MCP Tools

### BDNS (Grants) - 3 tools

| Tool | Description |
|------|-------------|
| `search_grants` | Search grant calls by date range and granting body |
| `search_grant_awards` | Search awarded grants by date range and beneficiary NIF |
| `get_grant_details` | Get detailed information about a specific grant call |

### BOE (Legislation) - 11 tools

| Tool | Description |
|------|-------------|
| `search_legislation` | Search consolidated laws with filters (query, dates, department, legal range, matter) |
| `get_legislation_details` | Get metadata of a specific law or regulation (optionally with legal analysis) |
| `get_legislation_text` | Get full consolidated text of a law |
| `get_legislation_structure` | Get the structure/index of a law (articles, dispositions, annexes) |
| `get_legislation_block` | Get a specific block (article, disposition) from a law |
| `get_departments_table` | Get list of government departments with codes |
| `get_legal_ranges_table` | Get list of legal norm types (Ley, Real Decreto, etc.) |
| `get_matters_table` | Get list of subject matters/topics with codes |
| `find_related_laws` | Find laws related to a given legislation (modifications, repeals, references) |
| `search_recent_boe` | Search BOE publications from the last N days with filters |
| `get_boe_summary` | Get the daily BOE summary for a specific date (with filters) |

### BORME (Company Registry) - 1 tool

| Tool | Description |
|------|-------------|
| `get_borme_summary` | Get daily company registry acts for a specific date |

### INE (Statistics) - 6 tools

| Tool | Description |
|------|-------------|
| `get_ine_operations` | List all available statistical operations (IPC, EPA, PIB, etc.) |
| `get_ine_operation` | Get details of a specific statistical operation |
| `get_ine_table_data` | Get data from a specific statistical table |
| `get_ine_series_data` | Get time series data by series code |
| `search_ine_tables` | Search for tables within a statistical operation |
| `get_ine_variables` | List available variables, optionally filtered by operation |

### datos.gob.es (Open Data) - 4 tools

| Tool | Description |
|------|-------------|
| `search_open_data` | Search datasets in the national open data catalog |
| `get_open_data_details` | Get detailed information about a specific dataset |
| `list_open_data_themes` | List available themes/categories |
| `list_open_data_publishers` | List publishing organizations |

### General - 1 tool

| Tool | Description |
|------|-------------|
| `get_system_info` | Get overview of available data sources and tools |

---

## Example Queries for Claude

Here are practical examples of what you can ask Claude once the MCP is connected:

### Grants & Subsidies (BDNS)

```
"Find grants published in the last month"

"Search for grants related to innovation or R&D"

"What grants has the company with NIF B12345678 received?"

"Show me details of grant BDNS 123456"
```

### Legislation (BOE)

```
"Search for laws about renewable energy"

"What was published in the BOE today?"

"Find legislation about public subsidies from 2023"

"Show me the full text of the data protection law"
```

### Company Registry (BORME)

```
"What companies were registered in Madrid today?"

"Show me the BORME summary for January 15, 2024"

"Find recent company dissolutions"
```

### Statistics (INE)

```
"What statistical operations are available from INE?"

"Show me the latest CPI (IPC) data"

"Get unemployment statistics from the EPA survey"

"What is the current inflation rate in Spain?"

"Show me GDP growth data for the last 12 quarters"

"Find tables about population in the Census operation"
```

### Combined Research

```
"I want to investigate company XYZ. Check:
1. What grants have they received?
2. Any recent BORME entries about them?"

"Find all funding opportunities for renewable energy projects:
1. Current open grants
2. Relevant legislation"

"Give me an economic overview of Spain:
1. Latest unemployment rate (EPA)
2. Current inflation (IPC)
3. Recent GDP growth"
```

### Open Data (datos.gob.es)

```
"Search for datasets about air quality"

"Find open data from the Madrid city council"

"What data categories are available in datos.gob.es?"

"Show me details of dataset e05068001-mapas-estrategicos-de-ruido"
```

---

## Tool Parameters Reference

### search_grants
```json
{
  "date_from": "2024-01-01",    // Optional: Start date (YYYY-MM-DD)
  "date_to": "2024-12-31",      // Optional: End date (YYYY-MM-DD)
  "granting_body": "E00003901", // Optional: Granting body code
  "limit": 20                   // Optional: Max results (1-100, default 20)
}
```

### search_grant_awards
```json
{
  "date_from": "2024-01-01",      // Optional: Start date
  "date_to": "2024-12-31",        // Optional: End date
  "beneficiary_nif": "B12345678", // Optional: Beneficiary NIF/CIF
  "limit": 20                     // Optional: Max results
}
```

### get_grant_details
```json
{
  "grant_id": "123456"  // Required: BDNS grant ID
}
```

### search_legislation
```json
{
  "query": "energias renovables",  // Required: Search text
  "date_from": "2020-01-01",       // Optional: Start date
  "date_to": "2024-12-31",         // Optional: End date
  "title": "ley energia",          // Optional: Filter by title
  "department_code": "4225",       // Optional: Department code (use get_departments_table)
  "legal_range_code": "ley",       // Optional: Legal range (use get_legal_ranges_table)
  "matter_code": "170",            // Optional: Matter code (use get_matters_table)
  "include_derogated": false,      // Optional: Include repealed laws (default false)
  "offset": 0,                     // Optional: Skip results (pagination)
  "limit": 20                      // Optional: Max results (1-100)
}
```

### get_legislation_details
```json
{
  "legislation_id": "BOE-A-2015-10566"  // Required: BOE legislation ID
}
```

### get_legislation_text
```json
{
  "legislation_id": "BOE-A-2015-10566"  // Required: BOE legislation ID
}
```

### get_legislation_structure
```json
{
  "legislation_id": "BOE-A-2015-10566"  // Required: BOE legislation ID
}
```

### get_legislation_block
```json
{
  "legislation_id": "BOE-A-2015-10566", // Required: BOE legislation ID
  "block_id": "a1"                       // Required: Block ID (e.g., "a1" for article 1)
}
```

### get_departments_table
```json
{}  // No parameters required
```

### get_legal_ranges_table
```json
{}  // No parameters required
```

### get_matters_table
```json
{}  // No parameters required
```

### get_boe_summary
```json
{
  "date": "2024-01-15"  // Optional: Date (YYYY-MM-DD), defaults to today
}
```

### get_borme_summary
```json
{
  "date": "2024-01-15"  // Optional: Date (YYYY-MM-DD), defaults to today
}
```

### get_ine_operations
```json
{}  // No parameters required
```

### get_ine_operation
```json
{
  "operation_id": "IPC"  // Required: Operation ID or code (e.g., 'IPC', 'EPA', '25')
}
```

### get_ine_table_data
```json
{
  "table_id": "50902",  // Required: Table ID from INE
  "nult": 12            // Optional: Number of last periods (1-100, default 12)
}
```

### get_ine_series_data
```json
{
  "series_code": "IPC251856", // Required: Series code from INE
  "nult": 12                   // Optional: Number of last periods (1-100, default 12)
}
```

### search_ine_tables
```json
{
  "operation_id": "IPC"  // Required: Operation ID to search tables for
}
```

### get_ine_variables
```json
{
  "operation_id": "IPC"  // Optional: Filter variables by operation
}
```

### search_open_data
```json
{
  "query": "air quality",           // Optional: Search text
  "theme": "medio-ambiente",        // Optional: Theme code
  "publisher": "L01280796",         // Optional: Publisher ID
  "limit": 20                       // Optional: Max results (1-100)
}
```

### get_open_data_details
```json
{
  "dataset_id": "e05068001-mapas-estrategicos-de-ruido"  // Required: Dataset ID
}
```

### list_open_data_themes
```json
{}  // No parameters required
```

### list_open_data_publishers
```json
{
  "limit": 50  // Optional: Max results (default 50)
}
```

---

## Project Structure

```
src/public_radar/
├── common/          # HTTP client, dates, logging
├── sources/         # API clients (BDNS, BOE, INE, datos.gob.es)
│   ├── bdns.py      # BDNS client (grants)
│   ├── boe.py       # BOE client (legislation, BORME)
│   ├── ine.py       # INE client (statistics)
│   └── datos_gob.py # datos.gob.es client (open data)
├── mcp/             # MCP server and tools
│   ├── server.py    # MCP server + 26 tool handlers
│   └── logging.py   # Tool call logging (JSONL)
├── __init__.py
└── __main__.py      # CLI entry point

tests/
├── unit/            # Unit tests with mocks (168 tests)
├── integration/     # Real API tests (43 tests)
└── fixtures/        # Sample API responses
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_HOST` | Host to bind SSE server | `0.0.0.0` |
| `MCP_PORT` | Port for SSE server | `8080` |
| `MCP_LOGS_DIR` | Directory for tool call logs | `./logs` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Tool Call Logging

All MCP tool calls are logged to `logs/mcp_calls_YYYY-MM-DD.jsonl`:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "tool": "search_grants",
  "input": {"date_from": "2024-01-01", "limit": 10},
  "output_summary": {"count": 10, "first_title": "..."},
  "duration_ms": 450,
  "success": true,
  "error": null
}
```

Logs are automatically rotated (deleted after 7 days).

## Docker Deployment

```bash
# Start MCP server
docker-compose up -d

# Check health
curl http://localhost:8080/health

# View logs
docker-compose logs -f mcp

# Stop server
docker-compose down
```

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run linting
uv run pre-commit run --all-files

# Type checking
uv run mypy src/
```

### Current Test Coverage

- **211 tests passing** (168 unit + 43 integration)
- **53%+ code coverage** (unit tests only)
- Unit tests for all parsers and tool handlers
- Integration tests for real API calls (BDNS, BOE, INE, datos.gob.es)

## Data Sources

| Source | API | Description |
|--------|-----|-------------|
| BDNS | [Swagger](https://www.infosubvenciones.es/bdnstrans/doc/swagger) | National Grants Database |
| BOE | [Open Data](https://www.boe.es/datosabiertos/api/api.php) | Official Gazette & Legislation |
| INE | [API Manual](https://www.ine.es/dyngs/DataLab/manual.html?cid=45) | National Statistics Institute |
| datos.gob.es | [API Data](https://datos.gob.es/apidata) | National Open Data Catalog |

## Troubleshooting

### Claude Desktop doesn't see the MCP

1. Check the config file path is correct
2. Ensure `uv` is in your PATH
3. Verify the `cwd` path points to the project directory
4. Restart Claude Desktop completely

### API returns empty results

- BOE/BORME don't publish on weekends or holidays
- BDNS may have rate limits
- INE data is updated periodically (monthly, quarterly)

### Tool call errors

Check the logs at `logs/mcp_calls_YYYY-MM-DD.jsonl` for detailed error information.

## License

MIT
