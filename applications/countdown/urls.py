from django.urls import path

from . import views

app_name = 'countdown'

urlpatterns = [
    path('', views.index, name='index'),
    path('daily-card/preview/', views.daily_card_preview, name='daily_card_preview'),
    # Ruta canonical sin slash final (Meta es sensible al formato del media URL).
    path('daily-artifacts/<str:filename>', views.daily_artifact, name='daily_artifact'),
    # Compat legacy para URLs antiguas guardadas en BD.
    path('daily-artifacts/<str:filename>/', views.daily_artifact, name='daily_artifact_legacy'),
]
