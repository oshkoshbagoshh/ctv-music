from django.contrib import admin
from .models import (
    Genre, Artist, Album, Track, AdCampaign, ServiceRequest,
    PricingTier, License, Cart, CartItem, Order, OrderItem, UserProfile,
)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "genre")
    list_filter = ("genre",)
    search_fields = ("title", "artist__name")


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ("title", "album")
    search_fields = ("title", "album__title", "album__artist__name")


@admin.register(AdCampaign)
class AdCampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "starts_at", "ends_at")
    search_fields = ("name",)


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("email", "subject", "created_at")
    search_fields = ("email", "subject")


@admin.register(PricingTier)
class PricingTierAdmin(admin.ModelAdmin):
    list_display = ("name", "price_cents", "duration_months")
    search_fields = ("name",)


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ("id", "buyer", "track", "tier", "status", "created_at")
    list_filter = ("status", "tier")
    search_fields = ("buyer__username", "track__title")


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at")
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at", "reviewed_by", "reviewed_at")
    list_filter = ("status",)
    inlines = [OrderItemInline]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
