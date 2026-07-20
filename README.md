# Recruitment & Job Portal Backend (Django + Django REST Framework + JWT)

This repository contains the **backend** of the Recruitment & Job Portal application. The frontend is developed as a separate project and communicates with this service through a RESTful API.

---

# Project Architecture

The project follows a **multi-app architecture** to keep responsibilities separated and the codebase maintainable.

```text
config/           Project configuration (settings, URLs, ASGI/WSGI)
accounts/         Authentication, custom User model, user profiles, JWT
jobs/             Job categories and job postings
applications/     Job applications and application status history
core/             Shared permissions, dashboard APIs, statistics
```

---

# Accounts

A custom `User` model is used with **email-based authentication** instead of Django's default username login.

Each user has a `role` field with one of the following values:

* `jobseeker`
* `company`

A Django signal automatically creates the appropriate profile whenever a new user is registered.

### JobSeekerProfile

Stores information related to job seekers, including:

* Personal information
* Education history
* Skills
* Resume (uploaded file)
* Work experience

### CompanyProfile

Stores company information such as:

* Company name
* Description
* Website
* Industry
* Company logo

---

# Job Management

## JobCategory

Represents job categories such as:

* Software Development
* Marketing
* Design
* Finance

## JobPosting

Represents a job advertisement.

Each posting contains information including:

* Title
* Description
* Requirements
* Location
* Employment type
* Experience level
* Salary range
* Application deadline
* Status

Available statuses:

* `draft`
* `published`
* `closed`

---

# Search & Filtering

Job listings support filtering using **django-filter**.

Available filters include:

* Keyword
* Location
* Category
* Employment type
* Experience level
* Remote only
* Minimum salary
* Maximum salary

Sorting is also supported using the `ordering` parameter.

Example:

```text
/api/jobs/?ordering=-salary_max
```

---

# Job Applications

Each job seeker can submit **only one application per job posting**.

This rule is enforced using a database-level `UniqueConstraint`.

Application statuses:

* `pending`
* `reviewed`
* `shortlisted`
* `accepted`
* `rejected`
* `withdrawn`

---

# Application Status History

Every time a company changes an application's status, a history record is created.

Each record stores:

* Previous status
* New status
* User who made the change
* Timestamp

This provides a complete audit trail for every application.

---

# Dashboard & Statistics

## Company Dashboard

Provides statistics including:

* Total job postings grouped by status
* Total received applications grouped by status
* Most popular job postings

## Job Seeker Dashboard

Provides:

* Total submitted applications grouped by status
* Recent application activity

## Platform Overview

Provides global platform statistics such as:

* Total published jobs
* Total companies
* Total job seekers

---

# Authentication

Authentication is implemented using **JSON Web Tokens (JWT)** via
`djangorestframework-simplejwt`.

Configuration:

* Access Token lifetime: **60 minutes**
* Refresh Token lifetime: **7 days**

Security features:

* Refresh token rotation
* Blacklisting old refresh tokens after rotation

Additional JWT claims include:

* User role
* Email

This allows the frontend to determine the authenticated user's role without additional API requests.

---

# Permissions

Custom permissions are implemented inside `core/permissions.py`.

Available permission classes include:

* `IsJobSeeker`
* `IsCompany`
* `IsOwner`
* `IsJobOwnerCompany`

These ensure that users can only perform actions they are authorized to perform.

---

# Requirements

* Python 3.11+
* pip

---

# Installation

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate the environment

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Apply database migrations
python manage.py migrate

# Create an administrator account
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

The application will be available at:

```
http://127.0.0.1:8000/
```

Django Admin:

```
http://127.0.0.1:8000/admin/
```

For production deployments it is recommended to:

* Disable `DEBUG`
* Use a secure `SECRET_KEY`
* Switch from SQLite to PostgreSQL

---

# REST API

All endpoints are available under the `/api/` prefix.

## Authentication

| Method | Endpoint                     | Description                        |
| ------ | ---------------------------- | ---------------------------------- |
| POST   | `/api/auth/register/`        | Register a new user                |
| POST   | `/api/auth/login/`           | Obtain access & refresh tokens     |
| POST   | `/api/auth/refresh/`         | Generate a new access token        |
| POST   | `/api/auth/logout/`          | Blacklist the refresh token        |
| POST   | `/api/auth/change-password/` | Change password                    |
| GET    | `/api/auth/me/`              | Get authenticated user information |

---

## Profiles

| Method    | Endpoint                  | Description                                               |
| --------- | ------------------------- | --------------------------------------------------------- |
| GET/PATCH | `/api/profile/jobseeker/` | Retrieve or update the authenticated job seeker's profile |
| GET/PATCH | `/api/profile/company/`   | Retrieve or update the authenticated company's profile    |
| GET       | `/api/companies/<id>/`    | Public company profile                                    |

---

## Job Postings

| Method    | Endpoint                            | Description                                            |
| --------- | ----------------------------------- | ------------------------------------------------------ |
| GET       | `/api/jobs/`                        | List published job postings                            |
| GET       | `/api/jobs/?mine=1`                 | List job postings created by the authenticated company |
| POST      | `/api/jobs/`                        | Create a new job posting (companies only)              |
| GET       | `/api/jobs/<id>/`                   | Retrieve job details                                   |
| PUT/PATCH | `/api/jobs/<id>/`                   | Update a job posting                                   |
| DELETE    | `/api/jobs/<id>/`                   | Delete a job posting                                   |
| GET       | `/api/jobs/categories/`             | List all job categories                                |
| GET       | `/api/jobs/companies/<company_id>/` | Published jobs for a specific company                  |

### Available Query Parameters

* `keyword`
* `location`
* `category`
* `job_type`
* `experience_level`
* `is_remote`
* `salary_min`
* `salary_max`
* `ordering`

Example:

```text
/api/jobs/?keyword=django&location=Tehran&ordering=-salary_max
```

---

## Applications

| Method | Endpoint                      | Description                                                                      |
| ------ | ----------------------------- | -------------------------------------------------------------------------------- |
| POST   | `/api/applications/`          | Submit a new application                                                         |
| GET    | `/api/applications/`          | List applications (job seeker: own applications, company: received applications) |
| GET    | `/api/applications/?job=<id>` | Applications submitted for a specific job                                        |
| GET    | `/api/applications/<id>/`     | Retrieve application details including status history                            |
| PATCH  | `/api/applications/<id>/`     | Update application status or internal notes                                      |
| DELETE | `/api/applications/<id>/`     | Withdraw an application (if not finalized)                                       |

---

## Dashboards

| Method | Endpoint                    | Description                     |
| ------ | --------------------------- | ------------------------------- |
| GET    | `/api/dashboard/company/`   | Company dashboard statistics    |
| GET    | `/api/dashboard/jobseeker/` | Job seeker dashboard statistics |
| GET    | `/api/dashboard/overview/`  | Platform-wide statistics        |

---

# Example Usage

```bash
# Register a company
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
-H "Content-Type: application/json" \
-d '{
  "email":"company@example.com",
  "username":"company",
  "password":"StrongPass123!",
  "password_confirm":"StrongPass123!",
  "role":"company"
}'

# Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
-H "Content-Type: application/json" \
-d '{
  "email":"company@example.com",
  "password":"StrongPass123!"
}'

# Create a job posting
curl -X POST http://127.0.0.1:8000/api/jobs/ \
-H "Authorization: Bearer <ACCESS_TOKEN>" \
-H "Content-Type: application/json" \
-d '{
  "title":"Backend Developer",
  "description":"...",
  "location":"Tehran",
  "job_type":"full_time",
  "status":"published"
}'
```

---

# Technical Notes

### File Uploads

Uploaded files (resumes, company logos, etc.) are stored inside the `media/`
directory during development.

For production, using cloud object storage such as **Amazon S3** is recommended.

---

### Cross-Origin Resource Sharing (CORS)

Since the frontend is hosted separately, `django-cors-headers` is configured.

Allowed frontend origins should be defined using the
`CORS_ALLOWED_ORIGINS` environment variable.

---

### Pagination

All list endpoints use **PageNumberPagination** with a default page size of **10**.

---

### Django Version

The project has been tested with a recent Django release.

If compatibility issues occur, pin the Django version in `requirements.txt`
(e.g. `Django~=5.0`).

---

# Frontend

The frontend is maintained as a separate project and consumes this REST API.

All endpoints return JSON responses.

Except for registration and login, authenticated requests must include:

```http
Authorization: Bearer <access_token>
```
