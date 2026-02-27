from django.urls import path

from . import views

app_name = 'poll'

urlpatterns = [
    path('submit/', views.vote_submit, name='submit'),
    path('api/result/', views.api_result, name='api_result'),
]
