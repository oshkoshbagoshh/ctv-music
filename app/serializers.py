from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Genre, Artist, Album, Track, AdCampaign, ServiceRequest, PricingTier, License, Cart, CartItem, Order, OrderItem, UserProfile


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ["id", "name", "image"]


class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    artist_id = serializers.PrimaryKeyRelatedField(queryset=Artist.objects.all(), source="artist", write_only=True)
    genre = GenreSerializer(read_only=True)
    genre_id = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all(), source="genre", allow_null=True, required=False, write_only=True)

    class Meta:
        model = Album
        fields = ["id", "title", "artist", "artist_id", "genre", "genre_id", "cover_image", "release_date"]


class TrackSerializer(serializers.ModelSerializer):
    album = AlbumSerializer(read_only=True)
    album_id = serializers.PrimaryKeyRelatedField(queryset=Album.objects.all(), source="album", write_only=True)

    class Meta:
        model = Track
        fields = ["id", "title", "album", "album_id", "audio_file", "duration_seconds"]


class AdCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdCampaign
        fields = ["id", "name", "video", "starts_at", "ends_at"]


class ServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = ["id", "email", "subject", "message", "created_at"]
        read_only_fields = ["created_at"]


class PricingTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingTier
        fields = ["id", "name", "price_cents", "duration_months", "allowed_usages"]


class LicenseSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    track_id = serializers.PrimaryKeyRelatedField(queryset=Track.objects.all(), source="track", write_only=True)
    tier = PricingTierSerializer(read_only=True)
    tier_id = serializers.PrimaryKeyRelatedField(queryset=PricingTier.objects.all(), source="tier", write_only=True)

    class Meta:
        model = License
        fields = [
            "id",
            "buyer",
            "track",
            "track_id",
            "tier",
            "tier_id",
            "status",
            "starts_at",
            "ends_at",
            "created_at",
        ]
        read_only_fields = ["buyer", "status", "created_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["buyer"] = request.user
        return super().create(validated_data)


class CartItemSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    track_id = serializers.PrimaryKeyRelatedField(queryset=Track.objects.all(), source="track", write_only=True)
    tier = PricingTierSerializer(read_only=True)
    tier_id = serializers.PrimaryKeyRelatedField(queryset=PricingTier.objects.all(), source="tier", write_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "track", "track_id", "tier", "tier_id", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at", "items"]


class OrderItemSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    tier = PricingTierSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "track", "tier", "price_cents_snapshot", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "status", "created_at", "reviewed_by", "reviewed_at", "review_notes", "items"]
        read_only_fields = ["user", "status", "created_at", "reviewed_by", "reviewed_at"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "user", "role"]
        read_only_fields = ["user"]
