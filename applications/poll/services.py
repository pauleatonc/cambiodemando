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
            'result_label': "Maomeno' nomá'",
            'good_dash': 0,
            'bad_dash': 502,
            'good_gap': 502,
            'bad_gap': 0,
            'circumference': 502,
            'offset_start': 0,
            'offset_red': 502,
            'good_pct_display': 0,
            'bad_pct_display': 0,
        }

    good_pct = round(good_count / total, 2)
    bad_pct = round(bad_count / total, 2)

    # Escala por % Mal (de mayor a menor)
    if bad_pct >= 0.80:
        result_label = 'Como las weas'
    elif bad_pct >= 0.60:
        result_label = 'Mal, pero podría ser peor'
    elif bad_pct >= 0.40:
        result_label = "Maomeno' nomá'"
    elif good_pct >= 0.80:
        result_label = 'La raja'
    elif good_pct >= 0.60:
        result_label = 'Dentro de todo bien'
    else:
        result_label = "Maomeno' nomá'"

    # Circunferencia del arco SVG (r=80) para stroke-dasharray
    circumference = 502
    good_dash = round(good_pct * circumference)
    bad_dash = circumference - good_dash
    good_gap = circumference - good_dash
    bad_gap = circumference - bad_dash
    offset_start = 0  # CSS rotate(-90deg) ya posiciona el inicio en las 12h
    offset_red = circumference - good_dash

    return {
        'good_count': good_count,
        'bad_count': bad_count,
        'total': total,
        'good_pct': good_pct,
        'bad_pct': bad_pct,
        'result_label': result_label,
        'good_dash': good_dash,
        'bad_dash': bad_dash,
        'good_gap': good_gap,
        'bad_gap': bad_gap,
        'circumference': circumference,
        'offset_start': offset_start,
        'offset_red': offset_red,
        'good_pct_display': int(round(good_pct * 100)),
        'bad_pct_display': int(round(bad_pct * 100)),
    }
