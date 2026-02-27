from django.shortcuts import render

from .constants import TARGET_DATE

# Importación tardía para evitar dependencia circular
def index(request):
    """Vista principal: imagen, título, texto, contador y bloque de encuesta."""
    from applications.poll.services import get_poll_result

    target_iso = TARGET_DATE.isoformat()
    poll_result = get_poll_result()
    poll_has_voted = request.session.get('poll_voted', False)

    return render(request, 'countdown/index.html', {
        'target_iso': target_iso,
        'title': 'Cambio de mando',
        'description': 'Cuenta regresiva hasta el 11 de marzo de 2030 a las 12:00.',
        'poll_result': poll_result,
        'poll_has_voted': poll_has_voted,
    })
