# OmniDeck

## Overview
OmniDeck is a Flask-based internal suite for managing OTM (Oracle Transportation Management) migration projects. It follows Domain-Driven Design (DDD) principles.

## Architecture
- **Backend**: Python/Flask (`ui/backend/app.py`)
- **Frontend**: Jinja2 templates + static files (`ui/frontend/`)
- **Entry point**: `run.py` (runs on `0.0.0.0:5000`)
- **Domain data**: JSON files in `domain/`
- **Metadata**: OTM table metadata in `metadata/`
- **Infra scripts**: OTM query/update scripts in `infra/`

## Key Modules
- **Painel de Migração**: Manage migration projects, groups, and items
- **Execução de Scripts**: Script execution with real-time feedback
- **Dashboard de Migração**: Migration progress dashboards
- **Central de Cadastros**: Consultant/client/project registry

## Tech Stack
- Python 3.12
- Flask 3.x
- Jinja2 templates
- WeasyPrint (PDF rendering)
- Markdown
- Requests (OTM HTTP integration)

## Running
```bash
python3 run.py
```
Runs on port 5000 with host 0.0.0.0.

## Deployment
Configured for autoscale deployment using gunicorn:
```
gunicorn --bind=0.0.0.0:5000 --reuse-port run:app
```
