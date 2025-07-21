from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('components/', views.components_view, name='components'),
    path('components/<str:component_type>/<int:component_id>/', views.component_detail_view, name='component_detail'),
    path('reviews/', views.reviews_view, name='reviews'),
    path('search/', views.search, name='search'),

    #AUTH URLS
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]