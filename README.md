# hyuabot-shuttle-timetable-updater

A one-time data loader that fetches Hanyang University ERICA campus shuttle bus data and populates the HYUabot database. Runs once at initial deployment.

## Overview

The job loads complete shuttle service data into three tables:

- `shuttle_route` — Route definitions
- `shuttle_stop` — Stop locations per route
- `shuttle_timetable` — Full departure timetables

Supports master-DB failover.

## Architecture

```
src/
├── main.py              # Entry point; loads routes, stops, and timetables
├── models.py            # SQLAlchemy ORM models (ShuttleRoute, ShuttleStop, ShuttleTimetable)
├── scripts/
│   ├── route.py         # Fetches shuttle route data
│   ├── route_stop.py    # Fetches stop information per route
│   └── timetable.py     # Inserts timetable records
└── utils/
    └── database.py      # PostgreSQL engine factory with master failover
```

## Requirements

- Python ≥ 3.12
- PostgreSQL

## Environment Variables

| Variable            | Description              |
|---------------------|--------------------------|
| `POSTGRES_ID`       | PostgreSQL username      |
| `POSTGRES_PASSWORD` | PostgreSQL password      |
| `POSTGRES_HOST`     | PostgreSQL host          |
| `POSTGRES_PORT`     | PostgreSQL port          |
| `POSTGRES_DB`       | PostgreSQL database name |

## Running Locally

```bash
pip install -e .

export POSTGRES_ID=postgres
export POSTGRES_PASSWORD=password
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=hyuabot

cd src && python main.py
```

## Docker

The container exits after a single run — trigger it as a Kubernetes Job or one-off container.

```bash
docker build -t hyuabot-shuttle-timetable-updater .

docker run --rm \
  -e POSTGRES_ID=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_HOST=host.docker.internal \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_DB=hyuabot \
  hyuabot-shuttle-timetable-updater
```

## Development

```bash
pip install -e .[lint]       # flake8
pip install -e .[typecheck]  # mypy
pip install -e .[test]       # pytest
```

```bash
python -m flake8 src/ tests/
python -m mypy src/ tests/
python -m pytest -v
```

Tests run against a PostgreSQL instance at `localhost:25432`.

## CI/CD

| Workflow | Trigger | Jobs |
|---|---|---|
| `code-check.yml` | Push to any branch except `main` | lint, typecheck, test |
| `deploy.yml` | PR merged to `main` (or manual dispatch) | Docker build → push to `localhost:5000` |

CI runners: self-hosted X64 Linux (code checks) · ARM64 Linux (Docker build).

## License

GPLv3
