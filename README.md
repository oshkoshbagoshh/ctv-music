# CTVMusic

## Music Sync Licensing for CTV & Legal Workflows

### Buillt with:

- Django 5
- Django REST Framework
- Django CORS Headers
- Pillow
- Python Dotenv
- Vite
- React JS
- Tailwind CSS

## Overview

- Django 5 + Django REST Framework API powering a music catalog and a licensing/commerce flow.
- Designed to pair with a React frontend (Vite) via CORS.
- Buyers can add tracks to a cart, checkout to create an order, and the Legal team reviews orders to issue licenses.

## Key Features

- Catalog: Genres, Artists, Albums, Tracks (with media upload paths).
- Pricing and Licensing: PricingTier, License issuance on order approval.
- Commerce: Cart and Order with status workflow (pending_review → approved/rejected).
- Roles: UserProfile with roles buyer, contributor, legal.
- REST API: DRF viewsets mounted under /api/.
- CORS: Configured for local Vite dev server.

### Quickstart

1) Install dependencies
   pip install -r requirements.txt

# or

pip install Django djangorestframework django-cors-headers Pillow python-dotenv

2) Create .env (optional but recommended)
   cp .env.example .env
   # tweak values as needed

3) Apply migrations
   python manage.py makemigrations
   python manage.py migrate

4) Create a superuser
   python manage.py createsuperuser

5) Run the dev server
   python manage.py runserver 0.0.0.0:8000

6) (Optional) Generate sample data
   python manage.py generate_fake_data

Frontend Integration (Vite)

- Default allowed origins include http://localhost:5173 and http://127.0.0.1:5173
- Cookies/session auth is enabled with CORS_ALLOW_CREDENTIALS = True
- For POST/PUT with session auth, include CSRF token as X-CSRFToken and ensure the origin is in CSRF_TRUSTED_ORIGINS

Example fetch from Vite (session-based)
fetch('http://localhost:8000/api/cart/', {
credentials: 'include',
headers: { 'Content-Type': 'application/json' }
});

Environment Variables (.env)

- DJANGO_DEBUG=true
- DJANGO_SECRET_KEY=dev-secret-change-me
- ALLOWED_HOSTS=localhost,127.0.0.1
- CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000
- DEVELOPER_EMAIL=developer@tfnms.co
- PEXELS_API_KEY= # optional

API Endpoints (selected)

- Catalog (public)
    - GET /api/genres/
    - GET /api/artists/ ; POST /api/artists/ (open in dev; restrict in prod)
    - GET /api/albums/ ; POST /api/albums/
    - GET /api/tracks/ ; POST /api/tracks/
    - GET /api/pricing-tiers/
- Service requests (public)
    - POST /api/service-requests/ { email, subject, message }
- Cart (auth required)
    - GET /api/cart/
    - POST /api/cart/add_item/ { track_id, tier_id, quantity }
    - POST /api/cart/remove_item/ { track_id, tier_id }
    - POST /api/cart/clear/
    - POST /api/cart/checkout/ → creates Order in pending_review
- Orders
    - Buyer: GET /api/orders/ (own)
    - Legal: GET /api/orders/ (all)
    - Legal: POST /api/orders/{id}/approve/ { review_notes? }
    - Legal: POST /api/orders/{id}/reject/ { review_notes }

Roles

- Create a UserProfile for each user and set role to buyer or legal.
- buyer: manage cart/checkout, view own orders.
- legal: review all orders, approve/reject, issues Licenses automatically on approval.

Development Notes

- Media uploads use MEDIA_ROOT; Pillow is required.
- For production, configure ALLOWED_HOSTS, CORS, and CSRF trusted origins appropriately.
- Public write endpoints are open for convenience in dev; restrict for production.

Documentation

- See docs/ for detailed guides:
    - docs/api.md — Endpoint reference with sample payloads
    - docs/backend-setup.md — Local setup and env vars
    - docs/frontend-integration.md — Using the API from Vite
    - docs/env.md — All supported env variables

Testing

- Tests live in app/tests.py
- Run with:
  python manage.py test

License

- See LICENSE (MIT by default).