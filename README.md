# PipelineGuard

A production-ready multiproduct pipeline scheduling, monitoring, and alerting system for petroleum/fuel distribution companies.

## Features
- **White Labeling**: Tenant-specific branding (logo, colors, login bg).
- **Real-time Pipeline Monitoring**: interactive Leaflet map with live flow/pressure updates.
- **Batch Tracking**: Monitor product batches in transit with ETA and position.
- **Ullage & Tank Monitoring**: Real-time storage utilization and low-ullage alerts.
- **Vessel Discharge**: Track marine terminal discharge progress.
- **Alert Engine**: Automated alerts via WebSockets and Email for business rules.
- **Data Ingestion API**: Robust DRF endpoints for external SCADA integration.

## Technical Stack
- **Backend**: Django 5.x, DRF, Django Channels, Celery
- **Database**: PostgreSQL (Docker) / SQLite (Local)
- **Real-time**: Redis Channel Layer
- **Frontend**: Tailwind CSS, HTMX, Alpine.js, Leaflet
- **Deployment**: Docker, docker-compose

## Quick Start (Local)

1. **Clone and Setup**:
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   ```

2. **Seed Demo Data**:
   ```bash
   python manage.py seed_data
   ```
   *Note: This creates an admin user (admin / admin) and a demo tenant (NNPC Retail).*

3. **Run Services**:
   You need Redis running for Channels and Celery.
   
   **Server**:
   ```bash
   python manage.py runserver
   ```
   
   **Celery Worker**:
   ```bash
   celery -A pipeline worker -l info
   ```
   
   **Celery Beat** (for alerts):
   ```bash
   celery -A pipeline beat -l info
   ```

## API Ingestion Example
External systems can push data using the Tenant API Key.
Headers: `X-API-KEY: <your-tenant-key>`

**Tank Telemetry**:
`POST /api/assets/tanks/ingest/`
```json
[
  { "tank_id": 1, "current_volume": 42500, "current_temperature": 31.2 }
]
```

## Docker Deployment
```bash
docker-compose up --build
```
The system will be available at `http://localhost:8000`.
Check `.env` for database and redis configurations.
