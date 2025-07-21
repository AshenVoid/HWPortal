from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('search/', views.search, name='search'),

    # Components
    path('components/', views.components_view, name='components'),
    path('components/<str:component_type>/<int:component_id>/', views.component_detail_view, name='component_detail'),

    # Reviews
    path('reviews/', views.reviews_view, name='reviews'),
    path('reviews/vote/', views.vote_review_ajax, name='vote_review_ajax'),

    #AUTH URLS
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]