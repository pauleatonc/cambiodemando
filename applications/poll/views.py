from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Vote
from .services import get_poll_result


def has_voted_today(request):
    """True si esta sesión ya votó hoy (según fecha del servidor, ej. America/Santiago)."""
    session_key = request.session.session_key
    if not session_key:
        return False
    today = timezone.now().date()
    return Vote.objects.filter(session_key=session_key, created_at__date=today).exists()


@require_http_methods(['POST'])
def vote_submit(request):
    """Recibe POST con 'option' (good|bad). Solo permite 1 voto por sesión por día."""
    option = request.POST.get('option', '').strip().lower()
    if option not in (Vote.OPTION_GOOD, Vote.OPTION_BAD):
        return redirect('countdown:index')

    # No crear sesión nueva aquí: rompe CSRF (el token del form es de la sesión anterior).
    # Si no hay session_key, guardamos el voto sin él (cuenta igual; sin límite 1/día para esa petición).
    session_key = request.session.session_key

    if session_key and has_voted_today(request):
        return redirect('countdown:index')

    Vote.objects.create(option=option, session_key=session_key)
    return redirect('countdown:index')


def api_result(request):
    """Devuelve JSON con conteos, porcentajes, result_label y has_voted."""
    result = get_poll_result()
    result['has_voted'] = has_voted_today(request)
    return JsonResponse(result)
