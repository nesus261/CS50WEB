import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Count

from .models import User, Post


def index(request):
    paginator = Paginator(Post.objects.order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    if not page_number:
        page_number = 1
    if request.user.is_authenticated:
        to_follow = User.objects.exclude(id__in=request.user.followed.all().values_list('id')).exclude(id=request.user.id).annotate(followers_count=Count('followers')).order_by('-followers_count')[:5]
    else:
        to_follow = User.objects.annotate(followers_count=Count('followers')).order_by('-followers_count')[:5]
    return render(request, "network/posts.html", {
        "posts": paginator.get_page(page_number),
        "to_follow": to_follow
    })


@login_required(login_url='login', redirect_field_name=None)
def followed_view(request):
    posts = []
    for post in Post.objects.order_by('-created_at'):
        if request.user.followed.filter(id=post.author.id):
            posts.append(post)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    if not page_number:
        page_number = 1
    if request.user.is_authenticated:
        to_follow = User.objects.exclude(id__in=request.user.followed.all().values_list('id')).exclude(id=request.user.id).annotate(followers_count=Count('followers')).order_by('-followers_count')[:5]
    else:
        to_follow = User.objects.annotate(followers_count=Count('followers')).order_by('-followers_count')[:5]
    return render(request, "network/posts.html", {
        "posts": paginator.get_page(page_number),
        "to_follow": to_follow
    })


def profile_view(request, user_id):
    user = User.objects.get(id=user_id)
    paginator = Paginator(Post.objects.filter(author=user).order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    if not page_number:
        page_number = 1
    if request.user.is_authenticated:
        to_follow = User.objects.exclude(id__in=request.user.followed.all().values_list('id')).exclude(id=request.user.id).annotate(followers_count=Count('followers')).order_by('-followers_count')[:5]
    else:
        to_follow = User.objects.annotate(followers_count=Count('followers')).order_by('-followers_count')[:5]
    return render(request, "network/profile.html", {
        "profile": user,
        "followed": request.user.followed.filter(id=user_id).first() if request.user.is_authenticated else False,
        "posts": paginator.get_page(page_number),
        "to_follow": to_follow
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        
        avatar = request.FILES["avatar"]

        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, avatar=avatar)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required(login_url='login', redirect_field_name=None)
def post_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        if data.get("content"):
            post = Post(author=request.user, content=data.get("content"))
            post.save()
            return JsonResponse({"message": "Post added correctly"}, status=201)
        return JsonResponse({"error": "Content cannot be empty"}, status=400)
    return JsonResponse({"error": "POST request required."}, status=404)


@login_required(login_url='login', redirect_field_name=None)
def edit_post_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            post = Post.objects.get(id=data.get('post'))
            if data.get("content"):
                if post.author != request.user:
                    return JsonResponse({"error": "That is not your post"}, status=400)
                post.content = data.get('content')
                post.save()
                return JsonResponse({"message": "Post edited correctly"}, status=201)
            return JsonResponse({"error": "Content cannot be empty"}, status=400)
        except:
            return JsonResponse({"error": "Content find post"}, status=404)
    return JsonResponse({"error": "POST request required."}, status=404)


@login_required(login_url='login', redirect_field_name=None)
def like_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        post = Post.objects.get(id=data.get("post"))
        if not post:
            return JsonResponse({"error": "Post does not exist"}, status=404)
        if data.get("like"):
            post.likes.add(request.user)
        elif request.user.liked.get(id=data.get("post")):
            post.likes.remove(request.user)
        return JsonResponse({"message": "Success"}, status=202)
    return JsonResponse({"error": "POST request required."}, status=404)


def follow_view(request):
    if request.method == "POST":
        user = User.objects.get(id=request.POST["id"])
        if request.user == user:
            return HttpResponseRedirect(reverse("profile", kwargs={ 'user_id': request.POST["id"]}))
        if request.user.followed.filter(id=request.POST["id"]).first():
            request.user.followed.remove(user)
        else:
            request.user.followed.add(user)
        return HttpResponseRedirect(reverse("profile", kwargs={ 'user_id': request.POST["id"]}))
    return HttpResponseRedirect(reverse("login"))