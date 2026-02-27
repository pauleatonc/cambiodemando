from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

from .models import Vote
from .services import get_poll_result

SESSION_KEY_VOTED = 'poll_voted'


def _get_poll_context(request):
    """Contexto común: resultado de la encuesta y si el usuario ya votó."""
    result = get_poll_result()
    result['has_voted'] = request.session.get(SESSION_KEY_VOTED, False)
    return result


@require_http_methods(['POST'])
def vote_submit(request):
    """Recibe POST con 'option' (good|bad), crea Vote y marca sesión. Redirige al inicio."""
    option = request.POST.get('option', '').strip().lower()
    if option not in (Vote.OPTION_GOOD, Vote.OPTION_BAD):
        return redirect('countdown:index')

    Vote.objects.create(option=option)
    request.session[SESSION_KEY_VOTED] = True
    return redirect('countdown:index')


def api_result(request):
    """Devuelve JSON con conteos, porcentajes, result_label y has_voted."""
    result = get_poll_result()
    result['has_voted'] = request.session.get(SESSION_KEY_VOTED, False)
    return JsonResponse(result)
