from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("categories", views.categories, name="categories"),
    path("category/<str:category>", views.category_view, name="category"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing/<str:id>", views.listing, name="listing"),
    path("purchased", views.purchased, name="purchased"),
    path("my_listings", views.my_listings, name="my_listings"),
    path("user/<str:username>", views.user_view, name="user"),

    path("create_listing", views.create_listing, name="create_listing"),
    path("bid_listing", views.bid_listing, name="bid_listing"),
    path("end_listing", views.end_listing, name="end_listing"),
    path("comment", views.comment_view, name="comment"),
]
