Backend setup guide

Prerequisites
- Python 3.11+
- pip, virtualenv (recommended)
- SQLite (default) or another DB configured via env vars

Install dependencies
- pip install -r requirements.txt
- or install individually: Django, djangorestframework, django-cors-headers, Pillow, python-dotenv

Environment
- Copy .env.example to .env and adjust as needed
- Important variables:
  - DJANGO_DEBUG=true
  - DJANGO_SECRET_KEY=change-me
  - ALLOWED_HOSTS=localhost,127.0.0.1
  - CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000
  - DEVELOPER_EMAIL=developer@tfnms.co

Database
- python manage.py makemigrations
- python manage.py migrate

Admin user
- python manage.py createsuperuser

Run server
- python manage.py runserver 0.0.0.0:8000

Media and static
- MEDIA_ROOT defaults to ./media; ensure the folder exists or Django will create it on upload
- STATIC_ROOT defaults to ./staticfiles; in development STATICFILES_DIRS includes ./static if present

Sample data
- python manage.py generate_fake_data
  - This management command populates genres, artists, albums, tracks, and pricing tiers for quick testing.

Roles and profiles
- Each user has a UserProfile with roles: buyer, contributor, legal
- Profiles are auto-created on user creation with role=buyer (via signals). Update roles in Django Admin for legal reviewers.

Security notes
- Public write access to catalog endpoints is enabled for dev convenience; restrict in production
- Update ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS, and CSRF_TRUSTED_ORIGINS for your deployment domain
