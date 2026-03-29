# BetaTrax

BetaTrax is a Django-based defect tracking workflow for beta testing. It supports three roles:
- Beta Tester: submit defect reports
- Product Owner: evaluate new defects and close fixed defects
- Developer: pick defects and work on fixes

## Tech Stack

- Python 3.13+
- Django
- Django REST Framework
- SQLite
- PDM (optional)

## Project Structure

- PJ3297: Django project settings and root URLs
- BetaTrax: app with models, views, serializers, templates, and routes
- db.sqlite3: local SQLite database

## Setup

Option A: with PDM

    pdm install
    pdm run python manage.py migrate
    pdm run python manage.py runserver

Option B: with venv and pip

    python -m venv .venv
    .venv\Scripts\activate
    pip install django djangorestframework
    python manage.py migrate
    python manage.py runserver

Open the app at:

    http://127.0.0.1:8000/

## Stakeholder Guide

### 1. Beta Tester

Goal:
- Submit a new defect report.

Where to go:
- Dashboard: /tester/
- Defect form: /tester/defectform/

What to do:
1. Open /tester/.
2. Click Add New Defect Report.
3. Fill in title, description, reproduce step, version, product, and betatester.
4. tester_email is optional.
5. Submit the form and confirm the success page.

Expected result:
- A new defect is created with status New.

### 2. Product Owner

Goal:
- Evaluate newly submitted defects and move them into active tracking.

Where to go:
- Dashboard: /owner/
- Evaluate list: /owner/evaluate/
- Update one defect: /owner/evaluate/<id>/

What to do:
1. Open /owner/ and enter the evaluate page.
2. Select a defect from the New defects list.
3. Set status to Open.
4. Set severity and priority.
5. Save using PUT or PATCH.

Expected result:
- Defect status changes from New to Open.
- Severity and priority are stored.

### 3. Developer

Goal:
- Pick an open defect, work on it, then mark it fixed.

Where to go:
- Dashboard: /developer/
- Assign endpoint: /developer/defects/<id>/assign/
- Fix endpoint: /api/defects/<id>/fix/

What to do:
1. Open /developer/.
2. Select an Open defect from your product list.
3. Confirm the status changes to Assigned.
4. Call PATCH /api/defects/<id>/fix/ when the fix is done.

Expected result:
- Defect is linked to the developer and becomes Assigned.
- After fix API call, status becomes Fixed.

## Main Routes

- Tester dashboard: /tester/
- Submit defect form: /tester/defectform/
- Submit success page: /defectform/success/
- Product owner dashboard: /owner/
- Evaluate new defects page: /owner/evaluate/
- Evaluate/update one defect: /owner/evaluate/<id>/
- Developer dashboard: /developer/
- Assign defect to developer: /developer/defects/<id>/assign/
- Mark defect fixed (API): /api/defects/<id>/fix/
- Mark defect resolved (API): /api/defects/<id>/resolve/

## Data Model Overview

Core entities:
- Product
- BetaTester
- Developer
- ProductOwner
- DefectReport

DefectReport includes:
- title, description, reproduce_step, version
- optional tester_email
- status, severity, priority
- relations to product, tester, owner, developer

Status lifecycle values defined in the model:
- New
- Open
- Assigned
- Fixed
- Resolved
- and additional optional states

## PBI Mapping

PBI-01 Submit defect report
- Implemented through tester dashboard and defect form create endpoint.
- Optional tester email is supported.
- Default status is New.

PBI-02 Evaluate and accept defect
- Product owner can view New defects and update status, severity, and priority.

PBI-03 Select defect to work on
- Developer sees open defects for related product.
- Selecting a defect sets status to Assigned and links developer.

PBI-04 Fix defect
- API endpoint exists to mark Assigned defects as fixed.

PBI-05 Close resolved defect
- API endpoint exists to mark Fixed defects as resolved.


