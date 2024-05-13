from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing, Bid, Comment

MINIMUM_PRICE_MARKUP = 0.05

def index(request):
    listings = []
    for listing in Listing.objects.all():
        if listing.winner:
            continue
        price = listing.bid.order_by('-offer').first()
        price = price.offer if price else listing.starting_price 
        listings.append({ 
            "l": listing, 
            "price": format(price, ".2f")
        })
    return render(request, "auctions/index.html",{
        "title": "Active Listings",
        "listings": listings
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def categories(request):
    return render(request, "auctions/categories.html",{
        "categories": [{ "value": choice[0], "name": choice[1] } for choice in Listing._meta.get_field('category').choices]
    })


def category_view(request, category):
    if category in [choice[0] for choice in Listing._meta.get_field('category').choices]:
        listings = []
        for listing in Listing.objects.filter(category=category):
            if listing.winner:
                continue
            price = listing.bid.order_by('-offer').first()
            price = price.offer if price else listing.starting_price 
            listings.append({ 
                "l": listing, 
                "price": format(price, ".2f")
            })
        return render(request, "auctions/index.html",{
            "title": f"Items from: {next(filter(lambda a: a[0] == category, Listing._meta.get_field('category').choices))[1]}", # get name of category 
            "listings": listings
        })


@login_required(login_url='login', redirect_field_name=None)
def watchlist(request):
    if request.method == "POST":
        listing = Listing.objects.get(id=request.POST["listing_id"])
        if listing.followers.filter(username=request.user.username):
            listing.followers.remove(request.user)
        else:
            listing.followers.add(request.user)
        return HttpResponseRedirect(reverse("listing", kwargs={ 'id': request.POST["listing_id"] }))
    else:
        listings = []
        for listing in request.user.watchlist.all():
            if listing.winner:
                continue
            price = listing.bid.order_by('-offer').first()
            price = price.offer if price else listing.starting_price 
            listings.append({ 
                "l": listing, 
                "price": format(price, ".2f") 
            })
        return render(request, "auctions/index.html",{
            "title": "Watchlist",
            "listings": listings
        })


def user_view(request, username):
    listings = []
    for listing in Listing.objects.filter(user=User.objects.get(username=username)):
        if listing.winner:
            continue
        price = listing.bid.order_by('-offer').first()
        price = price.offer if price else listing.starting_price 
        listings.append({ 
            "l": listing, 
            "price": format(price, ".2f")
        })
    return render(request, "auctions/index.html",{
        "title": f"Active {username.capitalize()}'s Listings",
        "listings": listings
    })


@login_required(login_url='login', redirect_field_name=None)
def purchased(request):
    listings = []
    for listing in request.user.winning.all():
        price = listing.bid.order_by('-offer').first()
        price = price.offer if price else listing.starting_price 
        listings.append({ 
            "l": listing, 
            "price": format(price, ".2f") 
        })
    return render(request, "auctions/index.html",{
        "title": "Purchased",
        "listings": listings
    })


@login_required(login_url='login', redirect_field_name=None)
def my_listings(request):
    listings = []
    for listing in request.user.listing.all():
        price = listing.bid.order_by('-offer').first()
        price = price.offer if price else listing.starting_price 
        listings.append({ 
            "l": listing, 
            "price": format(price, ".2f") 
        })
    return render(request, "auctions/index.html",{
        "title": "My listings",
        "listings": listings
    })


class CreateListing(forms.Form):
    title = forms.CharField(label='Title', max_length=32)
    image_url = forms.CharField(label='Image url', max_length=512, required=False)
    starting_price = forms.FloatField(label='Starting price', 
                                      widget=forms.NumberInput(attrs={ 'placeholder': '$' }))
    category = forms.ChoiceField(label='Category', choices=Listing._meta.get_field('category').choices)
    description = forms.CharField(label='Description', max_length=2048, 
                                  widget=forms.Textarea())
    

@login_required(login_url='login', redirect_field_name=None)
def create_listing(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
        form = CreateListing(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            listing = Listing(title=data["title"], 
                                image_url=data["image_url"], 
                                starting_price=float(format(data["starting_price"], ".2f")),
                                category=data["category"],
                                description=data["description"],
                                user=request.user)
            listing.save()
            return HttpResponseRedirect(reverse("listing", kwargs={ 'id': listing.id }))
    else:
        return render(request, "auctions/create_listing.html",{
            "form": CreateListing()
        })


class BidForm(forms.Form):
    id = forms.DecimalField(widget=forms.HiddenInput())
    offer = forms.FloatField(label='Your offer', 
                             widget=forms.NumberInput(attrs={ 'placeholder': 'Bid' }))


class CommentForm(forms.Form):
    listing_id = forms.DecimalField(widget=forms.HiddenInput())
    content = forms.CharField(label='', max_length=512, widget=forms.Textarea(attrs={ 'rows': '5' }))


def listing(request, id):
    try:
        listing = Listing.objects.get(id=id)
        count_bids = listing.bid.count()
        last_bid = listing.bid.order_by('-offer').first()
        price = last_bid.offer if last_bid else listing.starting_price
        min_offer = last_bid.offer+MINIMUM_PRICE_MARKUP if last_bid else listing.starting_price
    except:
        return render(request, "auctions/message.html",{
            "title": "404 Not found",
            "message": f"Not found listing with id: {id}"
        })
    bid_form = BidForm(initial={ 'id': id })
    bid_form.fields["offer"].widget.attrs['min'] = min_offer
    return render(request, "auctions/listing.html",{
        "id": id,
        "listing": listing,
        "price": format(price, ".2f"),
        "count_bids": count_bids,
        "your_last_bid": True if last_bid and last_bid.user.username == request.user.username else False,
        "your_listing": True if listing.user.username == request.user.username else False,
        "bid_form": bid_form,
        "watched": request.user.is_authenticated and 
                   listing.followers.filter(username=request.user.username),
        "comment_form": CommentForm(initial={ 'listing_id': id })
    })


@login_required(login_url='login', redirect_field_name=None)
def bid_listing(request):
    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            id = int(form.cleaned_data["id"])
            listing = Listing.objects.get(id=id)
            last_bid = listing.bid.order_by('-offer').first()
            min_offer = last_bid.offer+MINIMUM_PRICE_MARKUP if last_bid else listing.starting_price
            offer = form.cleaned_data["offer"]
            if offer >= min_offer:
                bid = Bid(listing=listing, 
                          offer=offer, 
                          user=request.user)
                bid.save()
                return HttpResponseRedirect(reverse("listing", kwargs={ 'id': form.cleaned_data["id"] }))
    return HttpResponseRedirect(reverse("index"))


@login_required(login_url='login', redirect_field_name=None)
def end_listing(request):
    if request.method == "POST":
        listing = Listing.objects.get(id=request.POST["listing_id"])
        if listing.user.username == request.user.username and (winner := listing.bid.order_by('-offer').first()):
            listing.winner = winner.user
            for follower in listing.followers.all():
                listing.followers.remove(follower)
            listing.save()
        return HttpResponseRedirect(reverse("listing", kwargs={ 'id': request.POST["listing_id"] }))


@login_required(login_url='login', redirect_field_name=None)
def comment_view(request):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(listing=Listing.objects.get(id=form.cleaned_data["listing_id"]),
                              user=request.user,
                              content=form.cleaned_data["content"])
            comment.save()
        return HttpResponseRedirect(reverse("listing", kwargs={ 'id': form.cleaned_data["listing_id"] }))
