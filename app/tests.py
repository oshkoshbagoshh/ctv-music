from datetime import date
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import (
    Genre, Artist, Album, Track, PricingTier,
    Cart, CartItem, Order, License, UserProfile,
)


def create_sample_track():
    genre = Genre.objects.create(name="Pop")
    artist = Artist.objects.create(name="Test Artist")
    album = Album.objects.create(title="Test Album", artist=artist, genre=genre)
    audio = SimpleUploadedFile("test.mp3", b"fake-audio-bytes", content_type="audio/mpeg")
    track = Track.objects.create(title="Test Track", album=album, audio_file=audio, duration_seconds=123)
    return track


def create_pricing_tier(name="Standard", months=12, price=999):
    return PricingTier.objects.create(name=name, duration_months=months, price_cents=price)


class CatalogTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.track = create_sample_track()
        self.tier = create_pricing_tier()

    def test_catalog_lists(self):
        for path in [
            "/api/genres/",
            "/api/artists/",
            "/api/albums/",
            "/api/tracks/",
            "/api/pricing-tiers/",
        ]:
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, status.HTTP_200_OK, msg=f"Failed GET {path}")


class ServiceRequestTests(APITestCase):
    def test_create_service_request(self):
        payload = {"email": "user@example.com", "subject": "Hello", "message": "Need help"}
        resp = self.client.post("/api/service-requests/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", resp.data)


class CartFlowTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="buyer", password="pass1234")
        # Profile should auto-create via signals with role=buyer
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
        self.client.login(username="buyer", password="pass1234")
        self.track = create_sample_track()
        self.tier = create_pricing_tier()

    def test_add_list_remove_clear_checkout(self):
        # Initially empty cart
        resp = self.client.get("/api/cart/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["items"], [])

        # Add item
        payload = {"track_id": self.track.id, "tier_id": self.tier.id, "quantity": 2}
        resp = self.client.post("/api/cart/add_item/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(resp.data["items"]), 1)
        self.assertEqual(resp.data["items"][0]["quantity"], 2)

        # Add same item again (should increment)
        resp = self.client.post("/api/cart/add_item/", {"track_id": self.track.id, "tier_id": self.tier.id, "quantity": 1}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["items"][0]["quantity"], 3)

        # Remove item
        resp = self.client.post("/api/cart/remove_item/", {"track_id": self.track.id, "tier_id": self.tier.id}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["items"], [])

        # Re-add and clear
        self.client.post("/api/cart/add_item/", payload, format="json")
        resp = self.client.post("/api/cart/clear/", {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["items"], [])

        # Add and checkout
        self.client.post("/api/cart/add_item/", payload, format="json")
        resp = self.client.post("/api/cart/checkout/", {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["status"], "pending_review")
        order_id = resp.data["id"]

        # Cart now empty
        resp = self.client.get("/api/cart/")
        self.assertEqual(resp.data["items"], [])

        # Buyer sees their order
        resp = self.client.get("/api/orders/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(any(o["id"] == order_id for o in resp.data))


class OrdersPermissionsTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Buyer user
        self.buyer = User.objects.create_user(username="buyer2", password="pass1234")
        # Legal user
        self.legal = User.objects.create_user(username="legal", password="pass1234")
        self.legal.profile.role = "legal"
        self.legal.profile.save()

        # Create order for buyer via cart/checkout
        self.client.login(username="buyer2", password="pass1234")
        track = create_sample_track()
        tier = create_pricing_tier()
        self.client.post("/api/cart/add_item/", {"track_id": track.id, "tier_id": tier.id, "quantity": 1}, format="json")
        resp = self.client.post("/api/cart/checkout/", {}, format="json")
        self.order_id = resp.data["id"]
        self.client.logout()

    def test_buyer_only_sees_own_orders(self):
        self.client.login(username="buyer2", password="pass1234")
        resp = self.client.get("/api/orders/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(any(o["id"] == self.order_id for o in resp.data))
        self.client.logout()

    def test_legal_sees_all_and_can_approve_reject(self):
        self.client.login(username="legal", password="pass1234")
        # Sees all orders
        resp = self.client.get("/api/orders/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(any(o["id"] == self.order_id for o in resp.data))

        # Approve order
        resp = self.client.post(f"/api/orders/{self.order_id}/approve/", {"review_notes": "ok"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["status"], "approved")
        # Licenses created
        self.assertGreaterEqual(License.objects.filter(buyer__username="buyer2").count(), 1)

        # Rejecting an approved order should fail 400
        resp = self.client.post(f"/api/orders/{self.order_id}/reject/", {"review_notes": "nah"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.client.logout()

    def test_buyer_cannot_approve(self):
        self.client.login(username="buyer2", password="pass1234")
        resp = self.client.post(f"/api/orders/{self.order_id}/approve", {"review_notes": "try"}, format="json")
        self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))


class ModelConstraintsTests(TestCase):
    def setUp(self):
        self.track = create_sample_track()
        self.tier = create_pricing_tier()
        self.user = User.objects.create_user(username="cuser", password="pass1234")
        self.cart, _ = Cart.objects.get_or_create(user=self.user)

    def test_pricing_tier_unique(self):
        PricingTier.objects.create(name="UniqueTier", duration_months=6, price_cents=100)
        with self.assertRaises(IntegrityError):
            PricingTier.objects.create(name="UniqueTier", duration_months=6, price_cents=200)

    def test_cart_item_unique(self):
        CartItem.objects.create(cart=self.cart, track=self.track, tier=self.tier, quantity=1)
        with self.assertRaises(IntegrityError):
            CartItem.objects.create(cart=self.cart, track=self.track, tier=self.tier, quantity=2)
