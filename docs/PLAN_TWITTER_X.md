# Plan: Publicar imagen diaria en X (Twitter)

Objetivo: que la plataforma genere la imagen (ya hecho), la publique en Instagram (ya hecho) y **además la publique en X (Twitter)**.

---

## 0. Correspondencia de credenciales X (Developer Portal → variables de entorno)

| En el portal de X Developers | Variable de entorno en el proyecto |
|------------------------------|------------------------------------|
| **Consumer Key** | `X_CONSUMER_KEY` |
| **Consumer Key Secret** (Consumer Secret) | `X_CONSUMER_SECRET` |
| **Access Token** | `X_ACCESS_TOKEN` |
| **Secreto del Token de Acceso** (Access Token Secret) | `X_ACCESS_TOKEN_SECRET` |
| **Bearer Token** | `X_BEARER_TOKEN` (opcional; la publicación usa OAuth 1.0a con las cuatro anteriores) |

Para publicar tweets con imagen se usan las **cuatro primeras** (OAuth 1.0a). El Bearer Token sirve para otros flujos (p. ej. lectura con solo aplicación); puedes dejarlo en el `.env` si lo usas en el futuro.

---

## 1. Estado actual

| Paso | Estado | Detalle |
|------|--------|---------|
| Generar imagen | ✅ Hecho | `DailyCardGenerator` → JPG en `media/daily_cards/` |
| Publicar en Instagram | ✅ Hecho | `InstagramPublisher` + Meta Graph API (image_url + caption) |
| Publicar en X (Twitter) | ❌ Por hacer | — |

Flujo del scheduler: `refresh_instagram_token` → `generate_daily_image` → `publish_daily_instagram`.

---

## 2. API de X (Twitter)

- **Crear post con imagen**: subir media y luego crear el post con el `media_id`.
- **Documentación**: [Tweeting media (v2)](https://developer.x.com/en/docs/tutorials/tweeting-media-v2), [Post Tweets](https://developer.x.com/en/docs/twitter-api/tweets/manage-tweets/api-reference/post-tweets), [Media upload v2](https://developer.x.com/en/docs/twitter-api/tweets/manage-tweets/api-reference/post-media-upload).
- **Autenticación**: OAuth 2.0 (Authorization Code + PKCE) o OAuth 1.0a. En algunos entornos el upload de media en v2 exige OAuth 1.0a; conviene probar con la cuenta que vayas a usar.
- **Límites**: según el tipo de cuenta de desarrollador (Free / Basic / Pro); revisar en el portal de X Developers.
- **Texto del post**: mismo mensaje que en Instagram (caption con `{dias}`, `{good_pct}`, `{bad_pct}`, `{result_label}`). Límite 280 caracteres; si el caption es largo, truncar o acortar solo para X.

---

## 3. Tareas a implementar

### 3.1 Configuración y credenciales

- [ ] Crear proyecto/app en [X Developer Portal](https://developer.x.com/) y obtener:
  - API Key y API Secret (Consumer Key/Secret).
  - Access Token y Access Token Secret (OAuth 1.0a), **o** Client ID + Client Secret para OAuth 2.0 y flujo para obtener/refrescar access token.
- [ ] Añadir en `settings/base.py` (o por entorno):
  - `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` (OAuth 1.0a), **o**
  - `X_CLIENT_ID`, `X_CLIENT_SECRET` y lógica de token OAuth 2.0 si se usa ese flujo.
- [ ] Documentar en `.env.example` las variables de X (sin valores reales).

### 3.2 Modelo de datos

- [ ] En `DailyPublication` añadir campos para X (migración):
  - `x_tweet_id` (CharField, blank) — ID del tweet publicado.
  - `x_published_at` (DateTimeField, null, blank) — opcional, para trazabilidad.
- [ ] Decisión: no hace falta un modelo tipo `InstagramTokenState` para X si usas tokens estáticos (OAuth 1.0a o token largo OAuth 2.0). Si más adelante implementas refresh de token OAuth 2.0, se puede añadir un modelo similar.

### 3.3 Publicador para X

- [ ] En `applications/poll/publication.py` (o nuevo módulo `x_publisher.py`):
  - Clase `XPublisher` (o `TwitterPublisher`) que:
    1. Reciba una `DailyPublication` con `image_path` (y opcionalmente `public_image_url` no usado para upload).
    2. **Suba la imagen**: leer el archivo desde `MEDIA_ROOT + publication.image_path`, llamar al endpoint de media upload de X (v2 o v1.1 según documentación y auth). Obtener `media_id`.
    3. **Construya el texto**: reutilizar la misma lógica que el caption de Instagram (`_caption(publication)`) pero asegurando ≤280 caracteres (truncar o template más corto solo para X).
    4. **Cree el post**: llamar al endpoint de creación de tweet/post con `media_ids=[media_id]` y el texto.
    5. Actualice la publicación: guardar `x_tweet_id` (y opcionalmente `x_published_at`) en `DailyPublication`; no cambiar `status` a “published” solo por X (o definir un criterio: “published” si al menos Instagram está OK y opcionalmente X).
- [ ] Autenticación: implementar OAuth 1.0a para las peticiones (por ejemplo con `requests-oauthlib`) o OAuth 2.0 si usas solo v2 y el upload lo permite.
- [ ] Tratamiento de errores: capturar excepciones, guardar mensaje en `last_error` (o campo dedicado para X) y no romper el flujo de Instagram.

### 3.4 Comando de gestión

- [ ] Nuevo comando `publish_daily_x` (o `publish_daily_twitter`):
  - Argumentos similares a `publish_daily_instagram`: `--date`, `--retries`, `--retry-delay`.
  - Buscar `DailyPublication` por fecha; si no hay imagen o ya tiene `x_tweet_id`, salir o avisar.
  - Instanciar `XPublisher` y llamar a `publish(publication)`.
  - Reintentos ante fallos transitorios (rate limit, 5xx).
- [ ] Opcional: comando único `publish_daily` que llame a Instagram y a X en secuencia (o en paralelo con cuidado con rate limits).

### 3.5 Scheduler

- [ ] En `run_daily_scheduler.py`, después de `publish_daily_instagram`:
  - Llamar a `call_command('publish_daily_x', date=current_date)` (o el nombre que elijas).
- [ ] Si X no está configurado (variables vacías), el comando `publish_daily_x` debe salir sin error (no-op) para no romper el cron.

### 3.6 Caption / texto para X

- [ ] Reutilizar el mismo template que Instagram (días, porcentajes, resultado) pero:
  - Asegurar longitud ≤280 caracteres (truncar o segundo template `X_CAPTION_TEMPLATE` más corto).
  - En el código del publicador X, construir el texto (por ejemplo desde `INSTAGRAM_CAPTION_TEMPLATE` o `X_CAPTION_TEMPLATE`) y pasar por el mismo `format(dias=..., good_pct=..., bad_pct=..., result_label=...)`.

### 3.7 Tests y documentación

- [ ] Tests unitarios para `XPublisher`: mock de la API (upload + create post), comprobar que se guarda `x_tweet_id` y que no se rompe ante 4xx/5xx.
- [ ] Actualizar README (o docs) con: requisitos de cuenta X, variables de entorno y pasos para publicar también en X.

---

## 4. Orden sugerido de implementación

1. **Configuración**: variables de entorno y settings (sin implementar aún la API).
2. **Modelo**: migración con `x_tweet_id` y `x_published_at`.
3. **XPublisher**: upload de media + create post (OAuth 1.0a recomendado para evitar problemas con media en v2), reutilizando caption y truncando a 280 caracteres.
4. **Comando** `publish_daily_x` con reintentos y salida silenciosa si X no está configurado.
5. **Scheduler**: añadir la llamada a `publish_daily_x` después de Instagram.
6. **Tests** y documentación.

---

## 5. Dependencias

- Añadir en `requirements.txt` (o el archivo de dependencias del proyecto) una librería para OAuth 1.0a con X si no la tienes, por ejemplo `requests-oauthlib` (junto con `requests`).

---

## 6. Resumen de archivos a tocar

| Archivo | Acción |
|---------|--------|
| `cambiodemando/settings/base.py` | Añadir variables `X_*` |
| `.env.example` | Documentar `X_*` |
| `applications/poll/models.py` | Añadir `x_tweet_id`, `x_published_at` |
| Nueva migración | Crear campos anteriores |
| `applications/poll/publication.py` (o nuevo módulo) | Clase `XPublisher` + caption ≤280 |
| `applications/poll/management/commands/publish_daily_x.py` | Nuevo comando |
| `applications/poll/management/commands/run_daily_scheduler.py` | Llamar a `publish_daily_x` |
| `applications/poll/admin.py` | Opcional: mostrar `x_tweet_id` / `x_published_at` en `DailyPublication` |
| Tests | Tests para `XPublisher` y comando |
| README o docs | Instrucciones X |

Cuando quieras, se puede bajar esto a tareas concretas por commit (por ejemplo: “solo settings y migración”, “solo XPublisher”, etc.).
