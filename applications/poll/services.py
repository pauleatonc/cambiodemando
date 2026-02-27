"""
Lógica de negocio de la encuesta.
Escala 20%: resultado según % Bien/Mal sobre el total.
"""
from django.db.models import Count

from .models import Vote


def get_poll_result():
    """
    Devuelve conteos, porcentajes y texto de resultado de la encuesta.
    Returns: dict con good_count, bad_count, total, good_pct, bad_pct, result_label.
    """
    agg = Vote.objects.values('option').annotate(count=Count('id'))
    counts = {r['option']: r['count'] for r in agg}
    good_count = counts.get(Vote.OPTION_GOOD, 0)
    bad_count = counts.get(Vote.OPTION_BAD, 0)
    total = good_count + bad_count

    if total == 0:
        return {
            'good_count': 0,
            'bad_count': 0,
            'total': 0,
            'good_pct': 0,
            'bad_pct': 0,
            'result_label': "maomeno' nomá'",
        }

    good_pct = round(good_count / total, 2)
    bad_pct = round(bad_count / total, 2)

    # Escala por % Mal (de mayor a menor)
    if bad_pct >= 0.80:
        result_label = 'Como las weas'
    elif bad_pct >= 0.60:
        result_label = 'mal, pero podría ser peor'
    elif bad_pct >= 0.40:
        result_label = "maomeno' nomá'"
    elif good_pct >= 0.80:
        result_label = 'La raja'
    elif good_pct >= 0.60:
        result_label = 'dentro de todo bien'
    else:
        result_label = "maomeno' nomá'"

    return {
        'good_count': good_count,
        'bad_count': bad_count,
        'total': total,
        'good_pct': good_pct,
        'bad_pct': bad_pct,
        'result_label': result_label,
    }
