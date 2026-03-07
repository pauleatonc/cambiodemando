from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('privacidad/', views.privacy, name='privacy'),
    path('acerca-de/', views.about, name='about'),
    path('contacto/', views.contact, name='contact'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('ads.txt', views.ads_txt, name='ads_txt'),
]
