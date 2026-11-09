FROM python:3.12-slim-bookworm

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# WeasyPrint (PDF invoices) needs Pango; gettext is needed for
# compilemessages (translations).
RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends \
        libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0 \
        libharfbuzz0b libgdk-pixbuf2.0-0 libffi8 shared-mime-info \
        fonts-dejavu-core gettext \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 1000 app

WORKDIR /code
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY --chown=app:app myshop/ /code/myshop/
WORKDIR /code/myshop

# Bake static files and compiled translations into the image.
RUN python manage.py collectstatic --noinput \
    && python manage.py compilemessages \
    && mkdir -p /code/myshop/media \
    && chown -R app:app /code/myshop

USER app
EXPOSE 8000

CMD ["gunicorn", "myshop.wsgi:application", \
     "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
