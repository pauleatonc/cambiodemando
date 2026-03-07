"""
Lógica de negocio de la encuesta.
Resultado según % Mal sobre el total, en tramos de 10%.
"""
from django.db.models import Count
from django.utils import timezone

from .models import Vote


# Tramos de 10% según proporción de votos "mal" (de mayor a menor).
# Cada tupla es (límite inferior de bad_pct, label).
# Ej.: si bad_pct >= 0.9 → "Cerremos por fuera"; si bad_pct >= 0.8 y < 0.9 → "Como las weas", etc.
RESULT_LABELS_BY_BAD_PCT = (
    (0.90, "Cerremos por fuera"),
    (0.80, "Como las weas"),
    (0.70, "Pá preocuparse"),
    (0.60, "Malena"),
    (0.50, "Maomeno' nomá'"),
    (0.40, "Piola"),
    (0.30, "Buena perrooo..."),
    (0.20, "Amerita piscolits"),
    (0.10, "Soñao"),
    (0.00, "Tamo' la raja"),  # 0–10% mal
)

DEFAULT_LABEL_NO_VOTES = "Maomeno'nomá'"


def _result_label_for_bad_pct(bad_pct):
    """Devuelve el label correspondiente al porcentaje de votos mal (0.0–1.0)."""
    for threshold, label in RESULT_LABELS_BY_BAD_PCT:
        if bad_pct >= threshold:
            return label
    return RESULT_LABELS_BY_BAD_PCT[-1][1]


def get_poll_result():
    """
    Devuelve conteos, porcentajes y texto de resultado de la encuesta.
    Returns: dict con good_count, bad_count, total, good_pct, bad_pct, result_label, etc.
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
            'result_label': DEFAULT_LABEL_NO_VOTES,
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
    result_label = _result_label_for_bad_pct(bad_pct)

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


def get_daily_poll_snapshot():
    """Payload estable para composición de imagen diaria y publicaciones."""
    result = get_poll_result()
    return {
        'snapshot_date': timezone.localdate(),
        'title': '¿Cómo vamos?',
        'result_label': result['result_label'],
        'good_count': result['good_count'],
        'bad_count': result['bad_count'],
        'total': result['total'],
        'good_pct_display': result['good_pct_display'],
        'bad_pct_display': result['bad_pct_display'],
        'good_dash': result['good_dash'],
        'bad_dash': result['bad_dash'],
        'good_gap': result['good_gap'],
        'bad_gap': result['bad_gap'],
        'circumference': result['circumference'],
        'offset_start': result['offset_start'],
        'offset_red': result['offset_red'],
    }
