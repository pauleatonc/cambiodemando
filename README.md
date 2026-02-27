# cambiodemando

Cuenta regresiva hasta el **11 de marzo de 2030** (12:00) y encuesta “¿Cómo vamos?” (Bien/Mal) con resultados persistentes.

- **Stack:** Django (monolito), PostgreSQL, Docker Compose.
- **Settings:** `cambiodemando.settings.dev` (desarrollo) y `cambiodemando.settings.prod` (producción).

## Desarrollo (Docker)

```bash
# Levantar servicios (Postgres + web con runserver)
docker compose up --build

# En otro terminal: migraciones ya se ejecutan al arrancar.
# App en http://localhost:8000/
```

Si el puerto 8000 está ocupado, edita `docker-compose.yml` y cambia `ports` (ej. `"8001:8000"`).

## Producción (Docker)

1. Definir variables de entorno (en `.env` o en el host):
   - `SECRET_KEY`: clave segura (obligatorio).
   - `ALLOWED_HOSTS`: hosts separados por coma (ej. `tudominio.com,www.tudominio.com`).
   - `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: credenciales de PostgreSQL.

2. Levantar:

```bash
docker compose -f docker-compose-prod.yml up --build -d
```

El comando del servicio `web` ejecuta `migrate`, `collectstatic` y gunicorn. Los estáticos se sirven con WhiteNoise.

## Sin Docker (local)

```bash
python -m venv .venv
source .venv/bin/activate   # o .venv\Scripts\activate en Windows
pip install -r requirements.txt

# Con SQLite (settings local)
export DJANGO_SETTINGS_MODULE=cambiodemando.settings.local
python manage.py migrate
python manage.py runserver
```

## Estructura

- `applications/countdown`: contador y página principal.
- `applications/poll`: encuesta y modelo `Vote`.
- `cambiodemando/settings/`: `base.py`, `local.py`, `dev.py`, `prod.py`.
