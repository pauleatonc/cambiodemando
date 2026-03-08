# 403 en upload.twitter.com (media upload)

## Qué se sabe

- **GET** `api.twitter.com/1.1/account/verify_credentials` → **200** (credenciales y app OK).
- **POST** `upload.twitter.com/1.1/media/upload.json` (INIT o simple upload) → **403**, cuerpo vacío, desde VPS y desde local.
- Conclusión: el bloqueo es **solo para el dominio upload.twitter.com** (o la capacidad de subir media), no por IP ni por firma OAuth.

## Qué revisar en developer.x.com

1. **Tu app** → **Settings** → **User authentication set up**
   - **App permissions**: debe ser **Read and write** (no "Read").
   - Después de cambiar, **regenerar** Access Token y Access Token Secret y actualizar `.env`.

2. **Products** / **Plan**
   - Comprueba si tu plan (Free / Basic / Pro) incluye **media upload** en la documentación actual de X.
   - En algunos planes el acceso a `upload.twitter.com` puede estar limitado o requerir “Elevated” / solicitud adicional.

3. **Restricciones**
   - En la app, revisa si hay **Restrict API access** o **IP allowlist** que pueda estar afectando solo a upload.

## Cómo contactar a X Developer Support

- **Dónde**: [X Developer Support](https://developer.x.com/en/support) o desde el portal (Help / Contact).
- **Qué pegar** (ajusta fechas si han pasado días):

```
App ID / nombre: [tu app]
Problema: 403 al subir media (upload.twitter.com), cuerpo vacío.

Hechos:
- GET https://api.twitter.com/1.1/account/verify_credentials.json → 200 OK (mismo OAuth 1.0a).
- POST https://upload.twitter.com/1.1/media/upload.json (INIT: command=INIT, total_bytes, media_type=image/jpeg) → 403, response body empty.
- Probado desde dos redes (VPS y local); mismo 403. Headers de respuesta incluyen: Server: cloudflare envoy, Content-Length: 0.

Pregunta: ¿Hay alguna restricción de plan o de app para usar upload.twitter.com (media upload)? ¿Debo activar algo en el portal o solicitar acceso adicional?
```

## Obtener más detalle del 403

Si al probar de nuevo con la app actualizada (y headers `Accept: application/json`) sigues recibiendo cuerpo vacío:

1. Prueba desde el navegador (o Postman) con la misma URL y método, si tienes forma de firmar OAuth 1.0a, para ver si la respuesta incluye HTML o JSON de error.
2. Vuelve a ejecutar con `--debug` por si en algún intento el servidor devuelve cuerpo:
   ```bash
   python manage.py publish_daily_x --debug
   ```
3. Revisa la [documentación actual de Media Upload](https://developer.x.com/en/docs/twitter-api/v1/media/upload-media/uploading-media/overview) por si hay requisitos nuevos de plan o de configuración.
