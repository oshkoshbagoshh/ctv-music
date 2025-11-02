from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Genre, Artist, Album, Track, AdCampaign, ServiceRequest, PricingTier, License, Cart, CartItem, Order, OrderItem
from .serializers import (
    GenreSerializer,
    ArtistSerializer,
    AlbumSerializer,
    TrackSerializer,
    AdCampaignSerializer,
    ServiceRequestSerializer,
    PricingTierSerializer,
    LicenseSerializer,
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
)
from .permissions import IsLegalReviewer, IsOwnerOrReadOnly


# Public read-only music catalog
class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all().order_by('name')
    serializer_class = ArtistSerializer
    permission_classes = [AllowAny]


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.select_related('artist', 'genre').all().order_by('title')
    serializer_class = AlbumSerializer
    permission_classes = [AllowAny]


class TrackViewSet(viewsets.ModelViewSet):
    queryset = Track.objects.select_related('album', 'album__artist').all().order_by('title')
    serializer_class = TrackSerializer
    permission_classes = [AllowAny]


class PricingTierViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PricingTier.objects.all().order_by('price_cents')
    serializer_class = PricingTierSerializer
    permission_classes = [AllowAny]


class ServiceRequestViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestSerializer
    permission_classes = [AllowAny]


# Cart and Orders
class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_cart(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    def list(self, request):
        cart = self.get_cart(request)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = self.get_cart(request)
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            track=serializer.validated_data['track'],
            tier=serializer.validated_data['tier'],
            defaults={'quantity': serializer.validated_data.get('quantity', 1)}
        )
        if not created:
            item.quantity += serializer.validated_data.get('quantity', 1)
            item.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        cart = self.get_cart(request)
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            item = CartItem.objects.get(
                cart=cart,
                track=serializer.validated_data['track'],
                tier=serializer.validated_data['tier'],
            )
        except CartItem.DoesNotExist:
            return Response({"detail": "Item not in cart"}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self.get_cart(request)
        cart.items.all().delete()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        cart = self.get_cart(request)
        if cart.items.count() == 0:
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user)
        for item in cart.items.select_related('track', 'tier').all():
            OrderItem.objects.create(
                order=order,
                track=item.track,
                tier=item.tier,
                price_cents_snapshot=item.tier.price_cents,
                quantity=item.quantity,
            )
        cart.items.all().delete()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if IsLegalReviewer().has_permission(self.request, self):
            # Legal can see all orders
            return Order.objects.all().order_by('-created_at')
        # Buyers see their own orders
        return Order.objects.filter(user=user).order_by('-created_at')

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsLegalReviewer])
    def approve(self, request, pk=None):
        order = self.get_object()
        if order.status != Order.Status.PENDING_REVIEW:
            return Response({"detail": "Order not pending review"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = Order.Status.APPROVED
        order.reviewed_by = request.user
        order.reviewed_at = timezone.now()
        order.review_notes = request.data.get('review_notes', '')
        order.save()
        # Issue licenses for each item
        for item in order.items.select_related('track', 'tier').all():
            License.objects.create(
                buyer=order.user,
                track=item.track,
                tier=item.tier,
                status=License.Status.ACTIVE,
                starts_at=timezone.now().date(),
                ends_at=None,
            )
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsLegalReviewer])
    def reject(self, request, pk=None):
        order = self.get_object()
        if order.status != Order.Status.PENDING_REVIEW:
            return Response({"detail": "Order not pending review"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = Order.Status.REJECTED
        order.reviewed_by = request.user
        order.reviewed_at = timezone.now()
        order.review_notes = request.data.get('review_notes', '')
        order.save()
        return Response(OrderSerializer(order).data)
