import json
from pathlib import Path
from urllib import error, parse, request

from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from applications.countdown.views import _get_daily_card_context

from .models import DailyPublication


class DailyCardGenerator:
    """Genera el JPG diario desde la vista/template de composicion."""

    width = 1080
    height = 1350

    def _load_css(self):
        css_path = Path(settings.BASE_DIR) / 'applications' / 'countdown' / 'static' / 'countdown' / 'daily_card.css'
        return css_path.read_text(encoding='utf-8')

    def _render_html(self):
        context = _get_daily_card_context()
        context['inline_css'] = self._load_css()
        html = render_to_string('countdown/daily_card.html', context)
        return html, context

    def _capture_screenshot(self, html, out_path):
        from playwright.sync_api import sync_playwright  # import tardio para no romper entornos sin dependencia

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': self.width, 'height': self.height, 'device_scale_factor': 1})
            page.set_content(html, wait_until='networkidle')
            page.screenshot(path=str(out_path), type='jpeg', quality=92, full_page=True)
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

    def __init__(self):
        self.base_url = settings.INSTAGRAM_BASE_URL.rstrip('/')
        self.access_token = settings.INSTAGRAM_ACCESS_TOKEN
        self.ig_user_id = settings.INSTAGRAM_IG_USER_ID

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
        template = settings.INSTAGRAM_CAPTION_TEMPLATE
        return template.format(
            good_pct=publication.good_pct_display,
            bad_pct=publication.bad_pct_display,
            result_label=publication.result_label,
        )

    def publish(self, publication):
        if publication.status == DailyPublication.STATUS_PUBLISHED:
            return publication

        if not self.access_token or not self.ig_user_id:
            raise RuntimeError('Faltan INSTAGRAM_ACCESS_TOKEN o INSTAGRAM_IG_USER_ID')
        if not publication.public_image_url:
            raise RuntimeError('La publicacion no tiene public_image_url')

        create_payload = {
            'image_url': publication.public_image_url,
            'caption': self._caption(publication),
            'access_token': self.access_token,
        }
        create_data = self._post(f'{self.ig_user_id}/media', create_payload)
        creation_id = create_data.get('id')
        if not creation_id:
            raise RuntimeError(f'Respuesta invalida create media: {create_data}')

        publish_data = self._post(
            f'{self.ig_user_id}/media_publish',
            {'creation_id': creation_id, 'access_token': self.access_token},
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
