"""
Constantes de la app countdown.
Fecha objetivo: 11 de marzo de 2030, 12:00 (mediodía) en America/Santiago.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

# 11 de marzo de 2030, 12:00 en Chile
TARGET_DATE = datetime(2030, 3, 11, 12, 0, 0, tzinfo=ZoneInfo('America/Santiago'))
