from django.urls import path

from . import views

app_name = 'countdown'

urlpatterns = [
    path('', views.index, name='index'),
    path('daily-card/preview/', views.daily_card_preview, name='daily_card_preview'),
    path('daily-artifacts/<str:filename>/', views.daily_artifact, name='daily_artifact'),
]
