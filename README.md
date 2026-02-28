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

## Publicación diaria en Instagram

Se implementó un flujo automático diario:
- Genera una imagen JPG (1080x1350) con base `static/img/kastfull.jpg` + resultado de la encuesta.
- Guarda artefacto y metadatos por fecha en `DailyPublication`.
- Publica en Instagram vía Meta Graph API.

### Variables de entorno nuevas

- `SITE_BASE_URL`: URL pública de la app (ej. `https://cambiodemando.cl`).
- `PUBLIC_MEDIA_BASE_URL`: base URL pública para servir los JPG diarios (si no está, usa `SITE_BASE_URL`).
- `INSTAGRAM_BASE_URL`: endpoint base de Graph API (por defecto `https://graph.facebook.com/v22.0`).
- `INSTAGRAM_ACCESS_TOKEN`: token de Instagram Graph API.
- `INSTAGRAM_IG_USER_ID`: ID de usuario de Instagram Business/Creator.
- `INSTAGRAM_APP_ID`: app id de Meta (requerido para inspección/refresh en Graph API).
- `INSTAGRAM_APP_SECRET`: app secret de Meta.
- `INSTAGRAM_REFRESH_MODE`: `facebook_exchange` (recomendado para cuenta profesional), `instagram_refresh` o `disabled`.
- `INSTAGRAM_REFRESH_THRESHOLD_DAYS`: umbral para refrescar antes de expirar.
- `INSTAGRAM_CAPTION_TEMPLATE`: plantilla del caption.
- `DAILY_POST_HOUR`: hora local de ejecución (por defecto `12`).
- `DAILY_POST_MINUTE`: minuto local de ejecución (por defecto `0`).

### Comandos de operación

```bash
# 1) Generar imagen del día
python manage.py generate_daily_image

# 2) Publicar imagen del día
python manage.py publish_daily_instagram

# 2.1) Inspeccionar / refrescar token manualmente
python manage.py refresh_instagram_token
python manage.py refresh_instagram_token --force

# 3) Ejecutar scheduler interno (loop diario)
python manage.py run_daily_scheduler

# 4) Probar flujo completo sin esperar al mediodía
python manage.py run_daily_scheduler --run-once
```

### Docker producción

`docker-compose-prod.yml` incluye ahora un servicio `scheduler` separado del `web`, para evitar duplicados por múltiples workers.
