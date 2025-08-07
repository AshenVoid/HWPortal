from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("search/", views.search, name="search"),
    # Components
    path("components/", views.components_view, name="components"),
    path(
        "components/<str:component_type>/<int:component_id>/",
        views.component_detail_view,
        name="component_detail",
    ),
    # Heureka API
    path(
        "heureka-data/<str:component_type>/<int:component_id>/",
        views.get_heureka_data,
        name="get_heureka_data",
    ),
    path(
        "heureka-price-history/<str:component_type>/<int:component_id>/",
        views.get_fake_price_history,
        name="get_heureka_price_history",
    ),
    path("track-heureka-click/", views.track_heureka_click, name="track_heureka_click"),
    # Reviews
    path("reviews/", views.reviews_view, name="reviews"),
    path("reviews/vote/", views.vote_review_ajax, name="vote_review_ajax"),
    path("review/create/", views.create_review_view, name="create_review"),
    path(
        "review/create/<str:component_type>/<int:component_id>/",
        views.create_review_for_component,
        name="create_review_for_component",
    ),
    path("get-components/", views.get_components_ajax, name="get_components_ajax"),
    path("review/edit/<int:review_id>/", views.edit_review_view, name="edit_review"),
    path(
        "review/delete/<int:review_id>/", views.delete_review_view, name="delete_review"
    ),
    path(
        "review/toggle-visibility/<int:review_id>/",
        views.toggle_review_visibility,
        name="toggle_review_visibility",
    ),
    path("get-user-votes/", views.get_user_votes, name="get_user_votes"),
    # Favorites
    path("favorites/", views.my_favorites_view, name="my_favorites"),
    path("favorites/toggle/", views.toggle_favorite_ajax, name="toggle_favorite_ajax"),
    path(
        "favorites/check/<str:component_type>/<int:component_id>/",
        views.check_favorite_status,
        name="check_favorite_status",
    ),
    path(
        "favorites/remove/<int:favorite_id>/",
        views.remove_favorite_view,
        name="remove_favorite",
    ),
    path("get-user-favorites/", views.get_user_favorites, name="get_user_favorites"),
    # Comparison URLs
    path("compare/", views.component_selector_view, name="component_selector"),
    path("compare/view/", views.component_comparison_view, name="component_comparison"),
    path("compare/add/", views.add_to_comparison, name="add_to_comparison"),
    path(
        "compare/remove/", views.remove_from_comparison, name="remove_from_comparison"
    ),
    path("compare/clear/", views.clear_comparison, name="clear_comparison"),
    # AUTH URLS
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    # User profile URLS
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),
    path("profile/password/", views.change_password_view, name="change_password"),
    path("profile/reviews/", views.my_reviews_view, name="my_reviews"),
]
