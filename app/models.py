import uuid
from pathlib import Path
from django.db import models
from django.conf import settings


def _uuid_filename(instance, filename: str, subdir: str) -> str:
    ext = Path(filename).suffix.lower()
    return f"{subdir}/{uuid.uuid4()}{ext}"


def artist_image_upload_to(instance, filename):
    return _uuid_filename(instance, filename, 'artists')


def album_cover_upload_to(instance, filename):
    return _uuid_filename(instance, filename, 'albums')


def track_audio_upload_to(instance, filename):
    return _uuid_filename(instance, filename, 'tracks')


def ad_video_upload_to(instance, filename):
    return _uuid_filename(instance, filename, 'ads')


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Artist(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to=artist_image_upload_to, blank=True, null=True)

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, related_name='albums')
    cover_image = models.ImageField(upload_to=album_cover_upload_to, blank=True, null=True)
    release_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} — {self.artist.name}"


class Track(models.Model):
    title = models.CharField(max_length=200)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='tracks')
    audio_file = models.FileField(upload_to=track_audio_upload_to)
    duration_seconds = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} — {self.album.artist.name}"


class AdCampaign(models.Model):
    name = models.CharField(max_length=200)
    video = models.FileField(upload_to=ad_video_upload_to, blank=True, null=True)
    starts_at = models.DateField(null=True, blank=True)
    ends_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class ServiceRequest(models.Model):
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email}: {self.subject}"


# --- Licensing / Commerce models ---

class UserProfile(models.Model):
    class Role(models.TextChoices):
        BUYER = 'buyer', 'Buyer'
        CONTRIBUTOR = 'contributor', 'Contributor'
        LEGAL = 'legal', 'Legal Reviewer'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.BUYER)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class PricingTier(models.Model):
    name = models.CharField(max_length=100)
    price_cents = models.PositiveIntegerField(default=0)
    duration_months = models.PositiveIntegerField(default=12)
    allowed_usages = models.TextField(blank=True)

    class Meta:
        unique_together = ("name", "duration_months")

    def __str__(self):
        return f"{self.name} (${self.price_cents / 100:.2f} / {self.duration_months}m)"


class License(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        EXPIRED = 'expired', 'Expired'
        REVOKED = 'revoked', 'Revoked'

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='licenses')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='licenses')
    tier = models.ForeignKey(PricingTier, on_delete=models.PROTECT, related_name='licenses')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    starts_at = models.DateField(null=True, blank=True)
    ends_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"License[{self.id}] {self.track.title} for {self.buyer} ({self.tier.name})"


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart({self.user})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    tier = models.ForeignKey(PricingTier, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "track", "tier")

    def __str__(self):
        return f"{self.track.title} x{self.quantity} ({self.tier.name})"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING_REVIEW = 'pending_review', 'Pending Review'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_REVIEW)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_orders')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order[{self.id}] {self.user} — {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    track = models.ForeignKey(Track, on_delete=models.PROTECT)
    tier = models.ForeignKey(PricingTier, on_delete=models.PROTECT)
    price_cents_snapshot = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"OrderItem[{self.id}] {self.track.title} ({self.tier.name}) x{self.quantity}"
