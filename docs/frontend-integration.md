Frontend integration (Vite + React)

Dev server origins
- Allowed by default: http://localhost:5173, http://127.0.0.1:5173
- To add more, set CORS_ALLOWED_ORIGINS in .env (comma-separated)

Session authentication
- Include credentials (cookies) in fetch/XHR
- For unsafe methods (POST/PUT/PATCH/DELETE), include CSRF token header X-CSRFToken
- Ensure your frontend origin is present in CSRF_TRUSTED_ORIGINS (derived from CORS list in settings.py)

Example: get cart (session)
```js
fetch('http://localhost:8000/api/cart/', {
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' }
}).then(r => r.json()).then(console.log);
```

Example: add to cart
```js
await fetch('http://localhost:8000/api/cart/add_item', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: JSON.stringify({ track_id, tier_id, quantity: 1 })
});
```

Login strategies
- Use Django admin for quick manual login during development.
- For production, add dedicated auth endpoints (e.g., dj-rest-auth, django-allauth, or custom views). This backend is compatible with token or session auth.
