# BetaTrax

BetaTrax is a Django defect-tracking workflow for beta testing teams.

It supports three role-based flows:
- Beta Tester: submit defect reports
- Product Owner: evaluate defects and manage lifecycle decisions
- Developer: assign defects and move them to fixed

## Features

- Defect submission form for testers
- Owner review page for new defects
- Developer dashboard to assign open defects
- REST API for defect lifecycle actions
- Comment API per defect (nested routes)
- SQLite-backed local development setup

## Tech Stack

- Python 3.13+
- Django
- SQLite

## Project Layout

- `PJ3297/`: project settings and root URL config
- `BetaTrax/`: app code (models, views, serializers, templates, URLs)
- `manage.py`: Django management entrypoint
- `db.sqlite3`: local database file

## Getting Started

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install django djangorestframework django-filter drf-nested-routers
```

### 3. Apply migrations

```powershell
python manage.py migrate
```

### 4. Run development server

```powershell
python manage.py runserver
```

Open: http://127.0.0.1:8000/

## Core Web Routes

- Tester dashboard: `/tester/`
- Defect submit form: `/tester/defectform/`
- Defect submit success page: `/defectform/success/`
- Product owner dashboard: `/owner/`
- Product owner evaluate page: `/owner/evaluate/`
- Product owner evaluate/update detail: `/owner/evaluate/<id>/`
- Developer dashboard: `/developer/`
- Developer assign action (POST): `/developer/defects/<id>/assign/`

## API Routes

- Defects CRUD and actions: `/api/defects/`
- Products CRUD: `/api/products/`
- New defects list: `/api/defects/new/`
- Defect detail: `/api/defects/<id>/`
- Defect comments (nested): `/api/defects/<id>/comments/`

Defect lifecycle custom actions (PATCH unless noted):
- Evaluate: `/api/defects/<id>/evaluate/`
- Assign (POST): `/api/defects/<id>/assign/`
- Fix: `/api/defects/<id>/fix/`
- Resolve: `/api/defects/<id>/resolve/`
- Reopen: `/api/defects/<id>/reopen/`
- Reject: `/api/defects/<id>/reject/`
- Mark duplicate: `/api/defects/<id>/mark_duplicate/`
- Cannot reproduce: `/api/defects/<id>/cannot_reproduce/`

## Defect Status Values

Supported status values:
- New
- Open
- Assigned
- CannotReproduce
- Fixed
- Reopened
- Resolved
- Rejected
- Duplicated

## Example API Calls

Mark defect as fixed:

```http
PATCH /api/defects/12/fix/
```

Resolve a fixed defect:

```http
PATCH /api/defects/12/resolve/
```

Assign a defect:

```http
POST /api/defects/12/assign/
```

## Notes

- Authentication and permissions are enforced for several API actions.
- Email notifications are sent through Django's console email backend in development.
- By default, list queries exclude defects with `Rejected` status unless filtered explicitly.


