from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import (
    GenreViewSet,
    ArtistViewSet,
    AlbumViewSet,
    TrackViewSet,
    PricingTierViewSet,
    ServiceRequestViewSet,
    CartViewSet,
    OrderViewSet,
)

router = DefaultRouter()
router.register(r'genres', GenreViewSet, basename='genre')
router.register(r'artists', ArtistViewSet, basename='artist')
router.register(r'albums', AlbumViewSet, basename='album')
router.register(r'tracks', TrackViewSet, basename='track')
router.register(r'pricing-tiers', PricingTierViewSet, basename='pricingtier')
router.register(r'service-requests', ServiceRequestViewSet, basename='servicerequest')
# Cart as non-model viewset
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    # Web views (optional; not used by Vite frontend)
    path('', views.home, name='home'),
    path('upload/artist/', views.upload_artist_image, name='upload_artist_image'),
    path('upload/album/', views.upload_album_cover, name='upload_album_cover'),
    path('upload/track/', views.upload_track_audio, name='upload_track_audio'),
    path('upload/ad/', views.upload_ad_video, name='upload_ad_video'),
    path('service-request/', views.service_request, name='service_request'),
    path('success/', views.upload_success, name='upload_success'),

    # API routes for React/Vite
    path('api/', include(router.urls)),
]
