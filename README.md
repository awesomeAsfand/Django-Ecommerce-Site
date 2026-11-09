# My Shop

A Django 5.2 e-commerce site built from chapters 8–11 of *Django 5 By
Example*: product catalog, session cart, orders, Stripe Checkout,
coupons, Redis-based recommendations, PDF invoices, and English/Spanish
translations.

## Stack

| Service   | What it does                                   | URL (dev)               |
|-----------|------------------------------------------------|-------------------------|
| `web`     | Django (runserver in dev, gunicorn in prod)    | http://localhost:8000   |
| `worker`  | Celery: order confirmation and invoice emails  |                         |
| `db`      | PostgreSQL 16                                  |                         |
| `cache`   | Redis: Celery broker and product recommendations |                       |
| `mailpit` | Catches every email sent in dev                | http://localhost:8025   |
| `flower`  | Celery monitor (profile `tools`)               | http://localhost:5555   |
| `stripe`  | Stripe CLI webhook forwarder (profile `stripe`) |                        |

## Local development

Requirements: Docker Desktop.

```bash
cp .env.example .env            # add your Stripe *test* keys
docker compose up --build       # http://localhost:8000
```

In a second terminal:

```bash
docker compose exec web python manage.py seed_shop        # sample products + coupon WELCOME10
docker compose exec web python manage.py createsuperuser  # admin at /en/admin/
```

The code in `myshop/` is bind-mounted, so edits reload automatically.
The Celery worker does **not** auto-reload: run
`docker compose restart worker` after changing `tasks.py`.

If port 8000 is already in use, set `WEB_PORT=8001` in `.env`.

### Payments (Stripe test mode)

1. Put your `sk_test_...`/`pk_test_...` keys in `.env`.
2. Start the webhook forwarder: `docker compose --profile stripe up -d stripe`
3. Copy the `whsec_...` secret from `docker compose logs stripe` into
   `STRIPE_WEBHOOK_SECRET` in `.env`, then `docker compose up -d web worker`.
4. Pay with card `4242 4242 4242 4242`, any future date, any CVC.

The webhook marks the order as paid, records the purchase for
recommendations, and emails a PDF invoice, which you can read in Mailpit.

### Common commands

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py shell
docker compose exec web python manage.py test
docker compose exec web python manage.py makemessages -l es   # then edit at /en/rosetta/
docker compose logs -f web worker
docker compose down          # stop (data is kept in volumes)
docker compose down -v       # stop and wipe the database
```

## Production (Docker)

```bash
cp .env.example .env    # DJANGO_DEBUG=0, real secret key, hosts, live Stripe keys, SMTP
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

* gunicorn listens on `127.0.0.1:8000`. Put a TLS reverse proxy (Caddy,
  nginx, Traefik) in front of it and set `DJANGO_CSRF_TRUSTED_ORIGINS`.
* WhiteNoise serves static files, which are collected at image build time.
* Uploaded product images are stored in the `media` volume.
* Migrations run automatically when `web` starts.
* Register `https://<your-domain>/payment/webhook/` in the Stripe
  dashboard for the `checkout.session.completed` event.

## Layout

```
myshop/                 Django project (manage.py lives here)
  shop/                 catalog, recommender, seed_shop command
  cart/                 session cart
  orders/               checkout, admin CSV export and PDF invoice
  payment/              Stripe Checkout and webhook
  coupons/              discount codes
  locale/               translations
book-reference/         original chapter 8-11 code, kept for reference
```
