from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=32)
    image_url = models.CharField(blank=True, max_length=512)
    starting_price = models.FloatField()
    CATEGORIES = [
        ("No Category Listed", "No category"),
        ("Fashion", "Fashion"),
        ("Electronics", "Electronics"),
        ("Cooking", "Cooking")
    ]
    category = models.CharField(
        max_length=18,
        choices=CATEGORIES,
        default="No Category Listed",
    )
    description = models.CharField(max_length=2048)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listing")
    created_at = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="winning", blank=True, null=True)
    followers = models.ManyToManyField(User, blank=True, related_name="watchlist")

    def __str__(self):
        return f"{self.title} ({self.user.username})"

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid")
    offer = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")

    def __str__(self):
        return f"{self.offer} for {self.listing.title} ({self.user.username})"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} in {self.listing.title}: ({self.content})"

