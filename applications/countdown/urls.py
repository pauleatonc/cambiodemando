from django.urls import path

from . import views

app_name = 'countdown'

urlpatterns = [
    path('', views.index, name='index'),
]
