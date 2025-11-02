# API Reference

Base URL: http://localhost:8000/api/

Authentication
- Public read for catalog and PricingTiers
- Session authentication (login via Django admin or a custom login view if added)
- For write operations that require auth, include credentials (cookies) and CSRF token

Catalog (public)
- GET /genres/
- GET /artists/ ; POST /artists/
- GET /albums/ ; POST /albums/
- GET /tracks/ ; POST /tracks/
- GET /pricing-tiers/

Service Requests (public)
- POST /service-requests/
  - Body: { "email": "user@example.com", "subject": "...", "message": "..." }
  - 201 Created on success

Cart (auth required)
- GET /cart/ → returns the current user's cart with items
- POST /cart/add_item
  - Body: { "track_id": <int>, "tier_id": <int>, "quantity": <int, default=1> }
  - 201 Created, returns updated cart
- POST /cart/remove_item
  - Body: { "track_id": <int>, "tier_id": <int> }
  - 200 OK, returns updated cart
- POST /cart/clear
  - 200 OK, returns empty cart
- POST /cart/checkout
  - 201 Created, returns the created Order with items and status pending_review

Orders (auth required)
- GET /orders/
  - Buyer: sees own orders only
  - Legal: sees all orders
- POST /orders/{id}/approve (legal only)
  - Body: { "review_notes": "..." } (optional)
  - 200 OK, returns updated Order, and Licenses are issued for each item
- POST /orders/{id}/reject (legal only)
  - Body: { "review_notes": "..." }
  - 200 OK, returns updated Order

Notes
- Public writes on catalog endpoints are open for development convenience; restrict in production.
- Licenses are issued with status ACTIVE on approval, with starts_at = today.
