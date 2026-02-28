import base64
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import render
from django.utils import timezone

from .constants import TARGET_DATE

# Importación tardía para evitar dependencia circular
def index(request):
    """Vista principal: imagen, título, texto, contador y bloque de encuesta."""
    from applications.poll.services import get_poll_result
    from applications.poll.views import has_voted_today

    # Forzar que la sesión se guarde y se envíe la cookie (evita 403 CSRF al votar)
    request.session.setdefault('_poll_visit', 1)

    target_iso = TARGET_DATE.isoformat()
    poll_result = get_poll_result()
    poll_has_voted = has_voted_today(request)

    return render(request, 'countdown/index.html', {
        'target_iso': target_iso,
        'title': 'Cambio de mando',
        'description': 'Cuenta regresiva hasta el 11 de marzo de 2030 a las 12:00.',
        'poll_result': poll_result,
        'poll_has_voted': poll_has_voted,
        'adsense_client': getattr(settings, 'ADSENSE_CLIENT', ''),
        'adsense_slot_inline_top': getattr(settings, 'ADSENSE_SLOT_INLINE_TOP', ''),
        'adsense_slot_inline_bottom': getattr(settings, 'ADSENSE_SLOT_INLINE_BOTTOM', ''),
        'adsense_slot_rail_left': getattr(settings, 'ADSENSE_SLOT_RAIL_LEFT', ''),
        'adsense_slot_rail_right': getattr(settings, 'ADSENSE_SLOT_RAIL_RIGHT', ''),
    })


def _get_daily_card_context():
    from applications.poll.services import get_daily_poll_snapshot

    image_path = Path(settings.BASE_DIR) / 'static' / 'img' / 'kastfull.jpg'
    image_bytes = image_path.read_bytes()
    image_b64 = base64.b64encode(image_bytes).decode('ascii')
    card_image_data_uri = f'data:image/jpeg;base64,{image_b64}'

    snapshot = get_daily_poll_snapshot()
    now = timezone.localtime()
    delta_days = (TARGET_DATE.date() - now.date()).days
    snapshot['card_image_data_uri'] = card_image_data_uri
    snapshot['days_to_change'] = max(0, delta_days)
    return snapshot


def daily_card_preview(request):
    """Vista dedicada para componer imagen diaria de publicacion."""
    context = _get_daily_card_context()
    return render(request, 'countdown/daily_card.html', context)


def daily_artifact(request, filename):
    """Sirve artefactos diarios para que Meta Graph API pueda descargar la imagen."""
    candidate = Path(settings.MEDIA_ROOT) / 'daily_cards' / filename
    if not candidate.exists() or not candidate.is_file():
        raise Http404('Archivo no encontrado')
    return FileResponse(candidate.open('rb'), content_type='image/jpeg')
