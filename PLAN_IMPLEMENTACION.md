# Plan de implementación: cambiodemando

Plataforma monolítica en Django (patrón MVC), PostgreSQL, despliegue con Docker Compose. Contador de días hasta una fecha objetivo y encuesta "¿Cómo vamos?" con resultados persistentes.

---

## 1. Resumen del proyecto

| Aspecto | Detalle |
|--------|---------|
| **Nombre** | cambiodemando |
| **Tipo** | Monolito Django |
| **Patrón** | MVC (Model-View-Controller / MVT en Django) |
| **Base de datos** | PostgreSQL |
| **Entornos** | dev (Docker), prod (Docker); local opcional más adelante |
| **Dependencias** | Un único `requirements.txt` |

---

## 2. Estructura de directorios objetivo

```
cambiodemando/
├── applications/
│   ├── __init__.py
│   ├── countdown/                    # App: contador hasta 11/03/2030 12:00
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                 # (vacío o solo config si no hay modelos)
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── templates/
│   │   │   └── countdown/
│   │   │       └── index.html
│   │   └── static/
│   │       └── countdown/
│   │           └── (imagen, css, js del contador)
│   └── poll/                         # App: encuesta "¿Cómo vamos?"
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py                 # Voto (opción, ip/session, timestamp)
│       ├── views.py
│       ├── urls.py
│       ├── templates/
│       │   └── poll/
│       │       └── (fragmentos o inclusión en home)
│       └── static/
│           └── poll/
│               └── (js para gráfico arco, estilos)
├── cambiodemando/                    # Proyecto Django
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py               # Exporta según DJANGO_SETTINGS_MODULE
│   │   ├── base.py                  # Config común (INSTALLED_APPS, MIDDLEWARE, etc.)
│   │   ├── local.py                 # Local (opcional, hereda de base)
│   │   ├── dev.py                   # Desarrollo (Docker), hereda de base
│   │   └── prod.py                  # Producción (Docker), hereda de base
│   ├── urls.py                      # Include de applications.countdown y applications.poll
│   ├── wsgi.py
│   └── asgi.py
├── templates/                        # Plantillas globales si se necesitan
│   └── base.html
├── static/
│   └── global/
├── requirements.txt
├── Dockerfile                        # Imagen única; settings vía variable de entorno
├── docker-compose.yml                # Dev → dev.py
├── docker-compose-prod.yml           # Prod → prod.py
├── .env.example
└── README.md
```

---

## 3. Fases de implementación

### Fase 1: Proyecto base y configuración

**1.1 Crear proyecto y estructura**

- Crear directorio raíz `cambiodemando` y entorno virtual (solo para generar proyecto si se desea; el desarrollo será en Docker).
- Crear proyecto Django: `django-admin startproject cambiodemando .` de modo que exista `cambiodemando/` con `manage.py` en la raíz.
- Crear carpeta `applications/` en la raíz y añadir `__init__.py`.
- Crear apps:
  - `python manage.py startapp countdown applications/countdown`
  - `python manage.py startapp poll applications/poll`
- Ajustar `applications/countdown/apps.py` y `applications/poll/apps.py` para que `name = 'applications.countdown'` y `name = 'applications.poll'`.

**1.2 Settings modular**

- Renombrar `cambiodemando/settings.py` a `cambiodemando/settings/base.py`.
- Crear `cambiodemando/settings/__init__.py` que, según `os.environ.get('DJANGO_SETTINGS_MODULE')`, importe y exporte el módulo correspondiente (o usar imports directos: `from .base import *` y en cada entorno sobrescribir/agregar).
- En `base.py`:
  - `INSTALLED_APPS`: incluir `'applications.countdown'`, `'applications.poll'`, y las apps estándar.
  - Configuración común: TIME_ZONE, USE_TZ, LANGUAGE_CODE, ROOT_URLCONF, WSGI_APPLICATION, templates, estáticos, etc.
  - No definir `SECRET_KEY` ni `DEBUG` ni `ALLOWED_HOSTS` ni `DATABASES` en base; hacerlo en cada entorno.
- `local.py`: DEBUG=True, ALLOWED_HOSTS=['localhost','127.0.0.1'], DATABASES SQLite o Postgres local, SECRET_KEY de desarrollo.
- `dev.py`: heredar de base; DEBUG=True; ALLOWED_HOSTS incluir 'web', 'localhost', '127.0.0.1'; DATABASES apuntando a servicio `db` de Docker (host=db, nombre, usuario y contraseña por variables de entorno); SECRET_KEY por variable de entorno.
- `prod.py`: heredar de base; DEBUG=False; ALLOWED_HOSTS desde variable de entorno; DATABASES igual que dev pero con credenciales de prod; SECRET_KEY y cualquier secreto por variable de entorno; seguridad (CSRF, cookies, etc.).

**1.3 Requirements**

- Un solo `requirements.txt`: Django, psycopg2-binary, gunicorn (para prod), y lo que se use para el gráfico (por ejemplo solo front: Chart.js o similar, sin dependencia server). No separar por ambiente.

**1.4 URLs del proyecto**

- En `cambiodemando/urls.py`:  
  - `path('', include('applications.countdown.urls'))`,  
  - `path('poll/', include('applications.poll.urls'))` (o la ruta que se defina para la encuesta).

---

### Fase 2: Docker (dev y prod)

**2.1 Dockerfile**

- Imagen base: `python:3.12-slim` (o 3.11).
- Instalar dependencias del sistema para psycopg2 si se usa `psycopg2` (no binary) en prod: `libpq-dev`, `gcc`.
- WORKDIR `/app`.
- Copiar `requirements.txt` y ejecutar `pip install -r requirements.txt`.
- Copiar el código del proyecto.
- Variable de entorno `DJANGO_SETTINGS_MODULE` se define en compose (no en Dockerfile) para elegir dev o prod.
- Comando por defecto: en dev puede ser `python manage.py runserver 0.0.0.0:8000`; en prod `gunicorn cambiodemando.wsgi:application --bind 0.0.0.0:8000`.

**2.2 docker-compose.yml (desarrollo)**

- Servicios:
  - `db`: imagen `postgres:16-alpine`, variables POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, volumen para persistencia.
  - `web`: build del Dockerfile, comando `runserver`, variable `DJANGO_SETTINGS_MODULE=cambiodemando.settings.dev`, depends_on db, ports 8000:8000, env_file o environment con DATABASE_URL o DB_HOST/USER/PASSWORD/NAME.
- Volumen para el código en `web` para desarrollo (montar código y recargar en caliente).

**2.3 docker-compose-prod.yml (producción)**

- Servicios:
  - `db`: postgres con credenciales de prod, volumen nombrado.
  - `web`: misma imagen, `DJANGO_SETTINGS_MODULE=cambiodemando.settings.prod`, comando gunicorn, depends_on db, sin montar código (copia en imagen).
- Solo variables de entorno de producción; sin DEBUG.

**2.4 Migraciones y arranque**

- En ambos compose, al levantar `web` ejecutar migraciones (entrypoint o comando: `python manage.py migrate && ...`) o documentar que el primer run debe incluir `migrate` y `collectstatic` en prod.

---

### Fase 3: App Countdown

**3.1 Contenido y lógica**

- Fecha objetivo fija: 11 de marzo de 2030, 12:00 (mediodía). Definir en settings (por ejemplo en `base.py` o en constantes del proyecto) o en la app countdown (p. ej. en `views` o en un `constants.py`).
- Vista principal: una sola view (p. ej. `index`) que renderice la plantilla con imagen, título, texto y contador.
- El contador (días, horas, minutos, segundos) puede calcularse en el servidor para el HTML inicial y actualizarse en el cliente con JavaScript cada segundo para no recargar la página.

**3.2 Template**

- Una sección con:
  - Imagen (una asset estática o URL configurable).
  - Título (ej. “Cambio de mando”).
  - Texto descriptivo.
  - Bloque para el contador: días, horas, minutos, segundos (por ejemplo con elementos `<span>` que JS actualice).
- Sin navbar ni login; diseño mínimo y responsive.

**3.3 Frontend del contador**

- JavaScript que, cada segundo, calcule la diferencia entre la fecha objetivo y “ahora” (en el timezone acordado, ej. America/Santiago) y actualice los 4 números. Considerar que la fecha objetivo sea la misma en el servidor y en el cliente (ej. ISO 2030-03-11T12:00:00).

**3.4 URLs**

- `applications/countdown/urls.py`: ruta `''` (o `'/'`) asociada a la view del countdown (página principal).

---

### Fase 4: App Poll (encuesta)

**4.1 Modelo de datos**

- Modelo `Vote` (o `PollVote`):
  - `option`: CharField con choices `[('good', 'Bien'), ('bad', 'Mal')]` (o similar).
  - `created_at`: DateTimeField(auto_now_add=True).
  - Opcional: identificador de sesión o IP (CharField, hasheado) para evitar votos duplicados por sesión; si no se requiere restricción, se puede omitir y permitir múltiples votos (según requisito: “votos acumulativos”).
- Migraciones: `python manage.py makemigrations poll` y aplicarlas en Docker.

**4.2 Lógica de negocio**

- Escala de resultado (20% sobre el total de votos):
  - % “Mal” ≥ 80% → “Como las weas”.
  - % “Mal” 60–80% → “mal, pero podría ser peor”.
  - % “Mal” 40–60% o empate → “maomeno' nomá'”.
  - % “Bien” 60–80% → “dentro de todo bien”.
  - % “Bien” ≥ 80% → “La raja”.
- Implementar una función (p. ej. en `services.py` o en el modelo) que, dado el total de votos y el conteo de “Bien”, devuelva el texto del resultado y los porcentajes.

**4.3 APIs o vistas**

- Vista que devuelva estado actual: si el usuario ya votó (si se usa sesión/cookie), conteos (Bien/Mal), porcentajes y texto de resultado. Puede ser una vista que renderice HTML con datos embebidos o un endpoint JSON para que el front pida datos y dibuje el gráfico.
- Vista (POST) para registrar voto: recibe “Bien” o “Mal”, crea `Vote`, opcionalmente guarda en sesión que ya votó, y redirige o devuelve JSON con el nuevo estado.
- Protección CSRF en formularios y en POST (Django por defecto).

**4.4 Integración en la página principal**

- En la misma view del countdown (o en una plantilla base), incluir debajo del contador:
  - Si no ha votado: botón/tarjeta “Encuesta” con la pregunta “¿Cómo vamos?” y dos botones “Bien” y “Mal”.
  - Si ya votó (o siempre, según diseño): sección con el gráfico en arco y debajo el texto del resultado según la escala anterior.
- El gráfico en arco puede implementarse con Chart.js (doughnut/pie con un solo segmento visible como arco) o con SVG/CSS. Mostrar porcentaje en el centro del arco o junto a él.

**4.5 URLs**

- `applications/poll/urls.py`: por ejemplo `submit/` para POST del voto, y si se usa API: `api/result/` para obtener resultado y porcentajes en JSON.

---

### Fase 5: Integración y presentación

**5.1 Flujo de la vista principal**

1. Usuario entra a la raíz del sitio.
2. Ve: imagen, título, texto, contador (días, horas, minutos, segundos).
3. Debajo: bloque de encuesta. Si no ha votado: pregunta “¿Cómo vamos?” y botones “Bien” / “Mal”. Al hacer clic se envía POST y se guarda el voto en la BD.
4. Tras votar (o si ya votó): se muestra el gráfico en arco con porcentajes y debajo el texto “Como las weas” / “mal, pero podría ser peor” / “maomeno' nomá'” / “dentro de todo bien” / “La raja” según la escala.

**5.2 Persistencia y sesión**

- Votos en PostgreSQL vía modelo `Vote`.
- Para “una vez se vote” y no volver a mostrar botones, usar sesión Django (o cookie): al votar se guarda en `request.session` un flag (ej. `poll_voted = True`) y en la template se comprueba para mostrar gráfico en lugar de botones. No es necesario login.

**5.3 Estilos y assets**

- CSS global o por app en `static/`. Imagen de la primera sección en `applications/countdown/static/countdown/` o en `static/global/`.
- Diseño simple y claro; el gráfico en arco legible (colores distintos para Bien/Mal, leyenda si se desea).

---

## 4. Orden sugerido de tareas (checklist)

- [x] **1** Crear estructura del proyecto Django y carpeta `applications/`.
- [x] **2** Crear apps `countdown` y `poll` dentro de `applications/` y configurar `INSTALLED_APPS` en `base.py`.
- [x] **3** Implementar `settings/base.py`, `dev.py`, `prod.py` y `__init__.py` en settings.
- [x] **4** Crear `requirements.txt` único.
- [x] **5** Configurar `cambiodemando/urls.py` con includes de ambas apps.
- [x] **6** Crear Dockerfile y docker-compose.yml (dev) con Postgres y `DJANGO_SETTINGS_MODULE=...dev`.
- [x] **7** Crear docker-compose-prod.yml con `DJANGO_SETTINGS_MODULE=...prod`.
- [x] **8** Documentar o automatizar migraciones y arranque (dev y prod).
- [x] **9** Implementar modelo `Vote` en `applications/poll`, migraciones.
- [x] **10** Implementar vista principal del countdown (imagen, título, texto, contador).
- [x] **11** Implementar template del countdown y JS del contador (días, horas, minutos, segundos).
- [x] **12** Implementar vistas de la encuesta: POST voto, vista/API resultado.
- [x] **13** Implementar lógica de escala (20%) y texto de resultado.
- [x] **14** Integrar encuesta en la misma página: botón “Encuesta”, formulario Bien/Mal, uso de sesión para “ya votó”.
- [x] **15** Implementar gráfico en arco (Chart.js o SVG) con porcentajes y texto de resultado debajo.
- [x] **16** Ajustar estilos y assets (imagen, responsividad).
- [x] **17** Probar en Docker (dev) y validar prod (compose-prod).

---

## 5. Notas técnicas

- **Timezone:** Definir en settings `TIME_ZONE` (ej. `America/Santiago`) y usar la misma zona en el JS para la fecha objetivo (ej. `2030-03-11T12:00:00` en esa zona).
- **CSRF:** En templates con POST incluir `{% csrf_token %}`; en peticiones AJAX enviar header o token CSRF según Django.
- **Seguridad prod:** En prod usar `SECRET_KEY` y credenciales por variables de entorno; no subir `.env` a repositorio; usar `.env.example` como plantilla.
- **Un único requirements.txt:** Todas las dependencias (Django, psycopg2-binary, gunicorn, etc.) en un solo archivo; las diferencias dev/prod se manejan por settings y por el comando ejecutado en Docker (runserver vs gunicorn).

Con este plan se puede implementar la plataforma “cambiodemando” de forma ordenada, con settings separados (local, dev, prod), dos apps bajo `applications/`, contador hasta el 11/03/2030 12:00, encuesta persistente en PostgreSQL y despliegue con Docker Compose para dev y prod.
