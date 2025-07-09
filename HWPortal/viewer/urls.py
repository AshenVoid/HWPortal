from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    #path('home/', views.home, name='home'),
    path('components/', views.components, name='components'),
    path('reviews/', views.reviews, name='reviews'),
    path('search/', views.search, name='search'),
]