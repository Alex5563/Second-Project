from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='jobs.index'),
    path('<int:id>/', views.show, name='jobs.show'),
    path('<int:id>/apply/', views.apply, name='jobs.apply'),
    path('manage/', views.manage, name='jobs.manage'),
    path('create/', views.create, name='jobs.create'),
]
