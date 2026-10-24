# Job Portal – Back-End

REST API for a job portal where **companies** publish job postings and **job seekers** search for them, apply and track the status of their applications.

Built with Django, Django REST Framework and JWT authentication. The matching client is in the `frontend` project (plain HTML/CSS/JavaScript, Persian RTL interface).

## Features

- Registration and login with email and password, JWT access/refresh tokens, refresh-token rotation and blacklist on logout
- Two roles, **job seeker** and **company**, with a profile created automatically for each user
- Job postings with draft / published / closed states, categories, remote option, salary range, application deadline
- Filtering, search, ordering and pagination of postings
- Applications with cover letter and resume upload, one application per job and applicant, withdrawal by the applicant
- Company-side status workflow (pending, reviewed, shortlisted, rejected, accepted), internal notes and a recorded status history
- Statistics endpoints for company, job seeker and the whole platform
- Django admin panel for all models

## Tech stack

| Part | Technology |
|---|---|
| Language / framework | Python 3.10+, Django 5.2 |
| API | Django REST Framework |
| Authentication | djangorestframework-simplejwt (with token blacklist) |
| Filtering | django-filter |
| CORS | django-cors-headers |
| Configuration | python-dotenv |
| Images | Pillow (company logo `ImageField`) |
| Database | SQLite (development) |

## Project structure

```
backend/
├── manage.py
├── config/            # settings.py, urls.py, wsgi.py
├── accounts/          # custom User, profiles, auth views, signals
├── jobs/              # job categories and postings, filters
├── applications/      # job applications and status history
├── core/              # permission classes and dashboard views
├── media/             # uploaded files (created at runtime)
└── db.sqlite3         # development database (created by migrate)
```

## Getting started

### 1. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install "django>=5.2,<5.3" djangorestframework djangorestframework-simplejwt \
            django-filter django-cors-headers python-dotenv pillow
```

### 2. Create the `.env` file

Create a `.env` file next to `manage.py`:

```env
DJANGO_SECRET_KEY=change-me-to-a-long-random-string
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

| Variable | Default | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | none | **Required.** The project does not define a fallback. |
| `DJANGO_DEBUG` | `True` | Debug mode. When true, CORS allows all origins and media files are served by Django. |
| `DJANGO_ALLOWED_HOSTS` | `*` | Comma-separated host list. |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Used when `DJANGO_DEBUG` is false. |

### 3. Create the database and an administrator

```bash
python manage.py migrate
python manage.py createsuperuser     # asks for email, username and password
```

### 4. Create job categories

Categories can only be created by the administrator, and the front-end job form requires the company to pick one (the API itself treats the category as optional). Start the server, open `http://127.0.0.1:8000/admin/`, and add a few entries under **Job Categories** (the slug is filled in automatically).

### 5. Run the server

```bash
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/api/`.

## Authentication

1. `POST /api/auth/login/` with `email` and `password` returns `access`, `refresh` and basic `user` data. The token also carries the `role` and `email` claims.
2. Send the access token with every request: `Authorization: Bearer <access>`.
3. Access tokens last **60 minutes**. Use `POST /api/auth/refresh/` with the refresh token to get a new one. Refresh tokens last **7 days**, are rotated on every refresh, and the old one is blacklisted.
4. `POST /api/auth/logout/` with the refresh token blacklists it.

Every endpoint requires authentication except registration and login.

## Roles and permissions

| Role | Can | Cannot |
|---|---|---|
| Job seeker | Browse published jobs, apply, list and view own applications, withdraw an application, edit own profile | Create postings, change application status |
| Company | Create, edit and delete own postings, list own postings including drafts, view applications to own postings, change status and notes, edit company profile | Apply to jobs, modify other companies' postings |
| Administrator | Manage everything in `/admin/` | – |

## API reference

All paths are relative to `/api/`.

### Auth and profiles

| Endpoint | Methods | Description |
|---|---|---|
| `auth/register/` | POST | Create an account (`email`, `username`, `password`, `password_confirm`, `role`, optional `phone_number`) |
| `auth/login/` | POST | Obtain tokens |
| `auth/refresh/` | POST | Obtain a new access token |
| `auth/logout/` | POST | Blacklist a refresh token |
| `auth/change-password/` | POST | `old_password`, `new_password` |
| `auth/me/` | GET | Current user |
| `profile/jobseeker/` | GET, PATCH | Job seeker profile (multipart for `resume_file`) |
| `profile/company/` | GET, PATCH | Company profile (multipart for `logo`) |
| `companies/{id}/` | GET | Company profile by id |

### Jobs

| Endpoint | Methods | Description |
|---|---|---|
| `jobs/` | GET, POST | List postings / create a posting (company) |
| `jobs/{id}/` | GET, PUT, PATCH, DELETE | Read, update or delete a posting (owner company only for changes) |
| `jobs/categories/` | GET | List categories (not paginated) |
| `jobs/companies/{company_id}/` | GET | Published postings of one company |

Query parameters for `GET jobs/`:

| Parameter | Description |
|---|---|
| `keyword` | Case-insensitive match in title, description and requirements |
| `search` | DRF search in title, description and location |
| `location` | Contains match on location |
| `category` | Category id |
| `job_type` | `full_time`, `part_time`, `contract`, `internship`, `remote` |
| `experience_level` | `entry`, `mid`, `senior`, `manager` |
| `is_remote` | `true` / `false` |
| `salary_min`, `salary_max` | `salary_min` ≥ value, `salary_max` ≤ value |
| `ordering` | `created_at`, `salary_min`, `salary_max`, `application_deadline` (prefix with `-` for descending) |
| `mine=1` | Company only: list all of its own postings, including drafts |
| `page` | Page number (10 items per page) |

Without `mine=1`, the list contains only **published** postings whose deadline has not passed.

### Applications

| Endpoint | Methods | Description |
|---|---|---|
| `applications/` | GET, POST | Own applications (job seeker) or applications to own postings (company); filter with `?job={id}`. POST creates an application (job seeker only) |
| `applications/{id}/` | GET, PATCH, DELETE | Details; change `status` and `company_notes` (company); withdraw (job seeker) |

### Dashboards

| Endpoint | Role | Returns |
|---|---|---|
| `dashboard/company/` | Company | Postings by status, applications by status, top postings by number of applications |
| `dashboard/jobseeker/` | Job seeker | Application counts by status and the 5 most recent applications |
| `dashboard/overview/` | Any | Open jobs, number of companies, number of job seekers |

## Example requests

```bash
# Register a company
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"hr@acme.com","username":"acme","password":"S3cure-pass!","password_confirm":"S3cure-pass!","role":"company"}'

# Log in
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"hr@acme.com","password":"S3cure-pass!"}'

# Create a published posting
curl -X POST http://127.0.0.1:8000/api/jobs/ \
  -H "Authorization: Bearer <access>" -H "Content-Type: application/json" \
  -d '{"title":"Backend Developer","description":"...","requirements":"...","responsibilities":"...",
       "category":1,"location":"Tehran","job_type":"full_time","experience_level":"mid",
       "status":"published","application_deadline":"2026-12-30"}'

# Search postings
curl "http://127.0.0.1:8000/api/jobs/?keyword=python&is_remote=true&ordering=-created_at" \
  -H "Authorization: Bearer <access>"

# Apply to a job (job seeker)
curl -X POST http://127.0.0.1:8000/api/applications/ \
  -H "Authorization: Bearer <access>" \
  -F job=1 -F cover_letter="I would like to apply" -F resume_snapshot=@resume.pdf

# Change an application's status (company)
curl -X PATCH http://127.0.0.1:8000/api/applications/1/ \
  -H "Authorization: Bearer <access>" -H "Content-Type: application/json" \
  -d '{"status":"shortlisted","company_notes":"Strong profile"}'
```

## Data model

| Model | Key fields | Relations |
|---|---|---|
| `User` | email (unique), username, role, phone_number, is_verified | – |
| `JobSeekerProfile` | first_name, last_name, birth_date, address, bio, education, skills, experience_years, resume_file | One-to-one with `User` |
| `CompanyProfile` | company_name, description, website, address, industry, logo, founded_year | One-to-one with `User` |
| `JobCategory` | name, slug | Has many postings |
| `JobPosting` | title, description, requirements, responsibilities, location, is_remote, job_type, experience_level, salary_min, salary_max, salary_is_visible, status, application_deadline, published_at | Belongs to a company `User` and an optional category |
| `JobApplication` | cover_letter, resume_snapshot, status, company_notes | Belongs to a posting and an applicant; unique on (job, applicant) |
| `ApplicationStatusHistory` | old_status, new_status, changed_by, changed_at | Belongs to an application |

A profile is created automatically (via a `post_save` signal) when a user registers.

## Validation and business rules

- `salary_min` cannot be greater than `salary_max`.
- A location is required unless the job is remote.
- A new posting cannot have a deadline in the past.
- Applications are accepted only for **published** postings whose deadline has not passed.
- A job seeker can apply to a given posting only once.
- Only the company that owns the posting can change an application's status or notes; every status change is recorded in the history.
- An application that is **accepted** or **rejected** cannot be withdrawn.
- `applications_count` on postings is shown only to the owning company (it is `0` for everyone else).

## Admin panel

Available at `/admin/`. It lists users (filter by role, verification and activity), both profile types, job categories, job postings (filters by status, type, level, remote and category) and applications, with the status history displayed read-only under each application.

## Uploaded files

Files are stored under `media/`:

- `resumes/user_<id>/` – profile resumes
- `company_logos/user_<id>/` – company logos
- `cover_letters/user_<id>/` – per-application resume files

With `DJANGO_DEBUG=True` Django serves them at `/media/`. In production, serve `media/` with your web server.

## Notes for production

- Set a strong `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False` and a specific `DJANGO_ALLOWED_HOSTS`.
- Set `CORS_ALLOWED_ORIGINS` to the real front-end origin(s).
- Use a production database (for example PostgreSQL), a WSGI server such as gunicorn, HTTPS, and serve static and media files from the web server.
- Run `python manage.py collectstatic` (static files go to `staticfiles/`).
