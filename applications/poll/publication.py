import json
from datetime import datetime, timedelta
from pathlib import Path
from urllib import error, parse, request

from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from applications.countdown.views import _get_daily_card_context
from applications.countdown.constants import TARGET_DATE

from .models import DailyPublication, InstagramTokenState


class DailyCardGenerator:
    """Genera el JPG diario desde la vista/template de composición."""

    width = 1080
    height = 1350

    # Requisitos Meta/Instagram para imágenes (Graph API):
    # - Formato: JPEG únicamente.
    # - Tamaño máximo: 8 MB.
    # - Espacio de color: sRGB (Chromium renderiza en sRGB por defecto).
    # - Relación de aspecto: entre 1.91:1 y 4:5 (1080×1350 = 4:5 ✓).
    JPEG_QUALITY_DEFAULT = 92
    META_MAX_IMAGE_BYTES = 8 * 1024 * 1024  # 8 MB

    def _load_css(self):
        css_path = Path(settings.BASE_DIR) / 'applications' / 'countdown' / 'static' / 'countdown' / 'daily_card.css'
        return css_path.read_text(encoding='utf-8')

    def _render_html(self):
        context = _get_daily_card_context()
        context['inline_css'] = self._load_css()
        html = render_to_string('countdown/daily_card.html', context)
        return html, context

    def _capture_screenshot(self, html, out_path):
        from playwright.sync_api import sync_playwright  # import tardío para no romper entornos sin dependencia

        quality = self.JPEG_QUALITY_DEFAULT
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': self.width, 'height': self.height, 'device_scale_factor': 1})
            page.set_content(html, wait_until='networkidle')
            page.screenshot(path=str(out_path), type='jpeg', quality=quality, full_page=True)
            browser.close()

        # Meta: máximo 8 MB. Si se supera, regenerar con menor calidad.
        for _ in range(3):
            size = out_path.stat().st_size
            if size <= self.META_MAX_IMAGE_BYTES:
                break
            quality = max(60, quality - 15)
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={'width': self.width, 'height': self.height, 'device_scale_factor': 1})
                page.set_content(html, wait_until='networkidle')
                page.screenshot(path=str(out_path), type='jpeg', quality=quality, full_page=True)
                browser.close()

    def generate(self, publication_date=None, force=False):
        publication_date = publication_date or timezone.localdate()
        filename = f'daily-card-{publication_date.isoformat()}.jpg'
        out_dir = Path(settings.MEDIA_ROOT) / 'daily_cards'
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / filename

        publication, _ = DailyPublication.objects.get_or_create(publication_date=publication_date)
        if out_path.exists() and not force and publication.image_path:
            return publication, out_path

        html, context = self._render_html()
        self._capture_screenshot(html, out_path)

        try:
            relative = out_path.relative_to(settings.BASE_DIR)
        except ValueError:
            relative = out_path
        public_url = f"{settings.PUBLIC_MEDIA_BASE_URL.rstrip('/')}{reverse('countdown:daily_artifact', kwargs={'filename': filename})}"
        publication.image_path = str(relative)
        publication.public_image_url = public_url
        publication.result_label = context['result_label']
        publication.good_count = context['good_count']
        publication.bad_count = context['bad_count']
        publication.total = context['total']
        publication.good_pct_display = context['good_pct_display']
        publication.bad_pct_display = context['bad_pct_display']
        publication.generated_at = timezone.now()
        publication.status = DailyPublication.STATUS_PUBLISH_PENDING
        publication.last_error = ''
        publication.save()
        return publication, out_path


class InstagramPublisher:
    """Publica una imagen diaria usando Meta Graph API (Instagram Business/Creator)."""

    # Caption por defecto si INSTAGRAM_CAPTION_TEMPLATE no está definido.
    # Placeholders: {dias}, {good_pct}, {bad_pct}, {result_label}
    DEFAULT_CAPTION = (
        '¿Cómo vamos? Guste o no, a nuestro presidente le quedan {dias} días en ejercicio. '
        'Participa en nuestra encuesta y cuéntanos tu opinión sobre su gestión.\n\n'
        'El sitio en la bio.'
        'Hoy: Bien {good_pct}% | Mal {bad_pct}% — {result_label}\n\n'
        'Los votos son acumulativos y se puede votar una vez por día. '        
    )

    def __init__(self):
        self.base_url = settings.INSTAGRAM_BASE_URL.rstrip('/')
        self.ig_user_id = settings.INSTAGRAM_IG_USER_ID
        self.token_manager = InstagramTokenManager()

    def _post(self, endpoint, payload):
        encoded = parse.urlencode(payload).encode('utf-8')
        req = request.Request(f'{self.base_url}/{endpoint.lstrip("/")}', data=encoded, method='POST')
        try:
            with request.urlopen(req, timeout=25) as resp:
                body = resp.read().decode('utf-8')
                return json.loads(body)
        except error.HTTPError as exc:
            detail = exc.read().decode('utf-8')
            raise RuntimeError(f'Graph API HTTP {exc.code}: {detail}') from exc
        except error.URLError as exc:
            raise RuntimeError(f'Graph API unreachable: {exc.reason}') from exc

    def _caption(self, publication):
        template = settings.INSTAGRAM_CAPTION_TEMPLATE or self.DEFAULT_CAPTION
        days_left = (TARGET_DATE.date() - publication.publication_date).days
        dias = max(0, days_left)
        return template.format(
            dias=dias,
            good_pct=publication.good_pct_display,
            bad_pct=publication.bad_pct_display,
            result_label=publication.result_label,
        )

    def publish(self, publication):
        if publication.status == DailyPublication.STATUS_PUBLISHED:
            return publication

        access_token = self.token_manager.get_active_token()
        if not access_token or not self.ig_user_id:
            raise RuntimeError('Faltan INSTAGRAM_ACCESS_TOKEN o INSTAGRAM_IG_USER_ID')
        if not publication.public_image_url:
            raise RuntimeError('La publicacion no tiene public_image_url')

        create_payload = {
            'image_url': publication.public_image_url,
            'caption': self._caption(publication),
            'access_token': access_token,
        }
        create_data = self._post(f'{self.ig_user_id}/media', create_payload)
        creation_id = create_data.get('id')
        if not creation_id:
            raise RuntimeError(f'Respuesta invalida create media: {create_data}')

        publish_data = self._post(
            f'{self.ig_user_id}/media_publish',
            {'creation_id': creation_id, 'access_token': access_token},
        )
        media_id = publish_data.get('id')
        if not media_id:
            raise RuntimeError(f'Respuesta invalida media publish: {publish_data}')

        publication.creation_id = creation_id
        publication.instagram_media_id = media_id
        publication.status = DailyPublication.STATUS_PUBLISHED
        publication.published_at = timezone.now()
        publication.last_error = ''
        publication.save()
        return publication


class InstagramTokenManager:
    """Gestiona inspeccion y refresh de token segun documentacion de Meta."""

    def __init__(self):
        self.base_url = settings.INSTAGRAM_BASE_URL.rstrip('/')
        self.app_id = settings.INSTAGRAM_APP_ID
        self.app_secret = settings.INSTAGRAM_APP_SECRET
        self.refresh_mode = settings.INSTAGRAM_REFRESH_MODE
        self.threshold_days = settings.INSTAGRAM_REFRESH_THRESHOLD_DAYS

    def _state(self):
        return InstagramTokenState.objects.order_by('id').first()

    def get_active_token(self):
        state = self._state()
        if state and state.access_token:
            return state.access_token
        return settings.INSTAGRAM_ACCESS_TOKEN

    def _save_state(self, **kwargs):
        state = self._state()
        if not state:
            state = InstagramTokenState()
        for key, value in kwargs.items():
            setattr(state, key, value)
        state.save()
        return state

    def _parse_timestamp(self, raw_value):
        if not raw_value:
            return None
        return datetime.fromtimestamp(int(raw_value), tz=timezone.utc)

    def _http_get_json(self, base_url, endpoint, params):
        query = parse.urlencode(params)
        url = f'{base_url.rstrip("/")}/{endpoint.lstrip("/")}?{query}'
        req = request.Request(url, method='GET')
        try:
            with request.urlopen(req, timeout=25) as resp:
                body = resp.read().decode('utf-8')
                return json.loads(body)
        except error.HTTPError as exc:
            detail = exc.read().decode('utf-8')
            raise RuntimeError(f'Graph API HTTP {exc.code}: {detail}') from exc
        except error.URLError as exc:
            raise RuntimeError(f'Graph API unreachable: {exc.reason}') from exc

    def inspect_token(self, token=None):
        token = token or self.get_active_token()
        if not token:
            raise RuntimeError('No hay token activo para inspeccionar')
        if not self.app_id or not self.app_secret:
            raise RuntimeError('Faltan INSTAGRAM_APP_ID o INSTAGRAM_APP_SECRET para debug_token')

        app_access_token = f'{self.app_id}|{self.app_secret}'
        response = self._http_get_json(
            self.base_url,
            'debug_token',
            {
                'input_token': token,
                'access_token': app_access_token,
            },
        )
        data = response.get('data') or {}
        expires_at = self._parse_timestamp(data.get('expires_at'))
        data_access_expires_at = self._parse_timestamp(data.get('data_access_expires_at'))
        self._save_state(
            access_token=token,
            expires_at=expires_at,
            data_access_expires_at=data_access_expires_at,
            token_type=data.get('type', ''),
            last_error='',
        )
        return data

    def _refresh_facebook_exchange(self, token):
        if not self.app_id or not self.app_secret:
            raise RuntimeError('Faltan INSTAGRAM_APP_ID o INSTAGRAM_APP_SECRET para facebook_exchange')

        response = self._http_get_json(
            self.base_url,
            'oauth/access_token',
            {
                'grant_type': 'fb_exchange_token',
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'fb_exchange_token': token,
            },
        )
        new_token = response.get('access_token')
        if not new_token:
            raise RuntimeError(f'Respuesta invalida al refrescar token: {response}')
        expires_in = int(response.get('expires_in', 0) or 0)
        expires_at = timezone.now() + timedelta(seconds=expires_in) if expires_in else None
        self._save_state(
            provider=InstagramTokenState.provider_facebook,
            access_token=new_token,
            refreshed_at=timezone.now(),
            expires_at=expires_at,
            last_error='',
        )
        return new_token, expires_at

    def _refresh_instagram_graph(self, token):
        response = self._http_get_json(
            'https://graph.instagram.com',
            'refresh_access_token',
            {
                'grant_type': 'ig_refresh_token',
                'access_token': token,
            },
        )
        new_token = response.get('access_token')
        if not new_token:
            raise RuntimeError(f'Respuesta invalida al refrescar token: {response}')
        expires_in = int(response.get('expires_in', 0) or 0)
        expires_at = timezone.now() + timedelta(seconds=expires_in) if expires_in else None
        self._save_state(
            provider=InstagramTokenState.provider_instagram,
            access_token=new_token,
            refreshed_at=timezone.now(),
            expires_at=expires_at,
            last_error='',
        )
        return new_token, expires_at

    def refresh_token(self, mode=None):
        mode = mode or self.refresh_mode
        if mode == 'disabled':
            return None
        token = self.get_active_token()
        if not token:
            raise RuntimeError('No hay INSTAGRAM_ACCESS_TOKEN para refrescar')

        try:
            if mode == 'instagram_refresh':
                return self._refresh_instagram_graph(token)
            return self._refresh_facebook_exchange(token)
        except Exception as exc:  # noqa: BLE001
            self._save_state(last_error=str(exc))
            raise

    def refresh_if_needed(self):
        if self.refresh_mode == 'disabled':
            return None
        state = self._state()
        # Sin metadatos previos: intentar inspeccion para tomar decision informada.
        if not state or not state.expires_at:
            try:
                data = self.inspect_token()
                expires_at = self._parse_timestamp(data.get('expires_at'))
            except Exception:
                # Si no se puede inspeccionar, refrescamos de todos modos para no quedarnos sin publicar.
                try:
                    return self.refresh_token()
                except Exception:
                    return None
        else:
            expires_at = state.expires_at

        if not expires_at:
            return None

        should_refresh = expires_at <= timezone.now() + timedelta(days=max(1, self.threshold_days))
        if should_refresh:
            return self.refresh_token()
        return None
