
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("profile/<str:user_id>", views.profile_view, name="profile"),
    path("followed", views.followed_view, name="followed"),
    
    path("post", views.post_view, name="post"),
    path("post-edit", views.edit_post_view, name="post-edit"),
    path("like", views.like_view, name="like"),
    path("follow", views.follow_view, name="follow")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
