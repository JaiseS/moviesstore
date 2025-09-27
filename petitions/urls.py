from django.urls import path
from . import views

app_name = 'petitions'

urlpatterns = [
    path('', views.petition_list, name='list'),
    path('create/', views.create_petition, name='create'),
    path('vote/<int:pk>/', views.vote_petition, name='vote'),
]
