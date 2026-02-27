from django.conf import settings
from django.shortcuts import render

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
