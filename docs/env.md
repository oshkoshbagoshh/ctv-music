Environment configuration

This project reads configuration from environment variables (optionally via a local .env file when python-dotenv is installed).

Core
- DJANGO_DEBUG: "true" or "false" (default: true)
- DJANGO_SECRET_KEY: Secret key for Django (use a strong unique value in production)
- ALLOWED_HOSTS: Comma-separated hosts (e.g., localhost,127.0.0.1,example.com)

CORS/CSRF
- CORS_ALLOWED_ORIGINS: Comma-separated list of allowed origins, e.g., http://localhost:5173,http://127.0.0.1:5173
  - CSRF_TRUSTED_ORIGINS is derived from this list in settings.py
- CORS_ALLOW_CREDENTIALS: True by default in settings; change in code if needed

Email/dev
- DEVELOPER_EMAIL: Address to receive ServiceRequest notifications (console backend in dev)

Third-party (optional)
- PEXELS_API_KEY: only used if you integrate with Pexels in custom code

Notes
- Update ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS, and CSRF_TRUSTED_ORIGINS when deploying.
- For production, set DJANGO_DEBUG=false and use a strong DJANGO_SECRET_KEY.
