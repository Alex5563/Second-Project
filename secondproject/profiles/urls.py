from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='profiles.index'),
    path('edit/', views.edit, name='profiles.edit'),
    path('privacy/', views.privacy, name='profiles.privacy'),
]