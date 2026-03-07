"""Context processors para templates (AdSense, verificación de sitio, datos globales)."""
from datetime import datetime

from django.conf import settings


def google_verification(request):
    """Expone códigos de verificación y AdSense para meta/script y bloques de anuncios."""
    return {
        'google_site_verification': getattr(settings, 'GOOGLE_SITE_VERIFICATION', ''),
        'adsense_client': getattr(settings, 'ADSENSE_CLIENT', ''),
        'adsense_slot_inline_top': getattr(settings, 'ADSENSE_SLOT_INLINE_TOP', ''),
        'adsense_slot_inline_bottom': getattr(settings, 'ADSENSE_SLOT_INLINE_BOTTOM', ''),
        'adsense_slot_rail_left': getattr(settings, 'ADSENSE_SLOT_RAIL_LEFT', ''),
        'adsense_slot_rail_right': getattr(settings, 'ADSENSE_SLOT_RAIL_RIGHT', ''),
        'ga_measurement_id': getattr(settings, 'GA_MEASUREMENT_ID', ''),
        'current_year': datetime.now().year,
        'social_instagram_url': getattr(settings, 'SOCIAL_INSTAGRAM_URL', '').strip() or None,
        'social_twitter_url': getattr(settings, 'SOCIAL_TWITTER_URL', '').strip() or None,
    }
