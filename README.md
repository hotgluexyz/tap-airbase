# tap-airbase

`tap-airbase` is a Singer tap for the [Airbase](https://www.airbase.io/) API.

## Installation

```bash
pipx install tap-airbase
```

## Configuration

```bash
tap-airbase --about
```

### Config options

| Setting | Required | Description |
|---------|----------|-------------|
| `api_key` | Yes | Airbase API key (sent as `Authorization: Token …`) |
| `sandbox` | No | Use the staging API (`api-stage.airbase.io`) |
| `start_date` | No | Reserved for future incremental sync |

## Usage

```bash
tap-airbase --version
tap-airbase --help
tap-airbase --config CONFIG --discover > ./catalog.json
```

## Development

```bash
pipx install poetry
poetry install
poetry run pytest
hotglue-smoke-test run
```
