from django import forms
from .models import Artist, Album, Track, AdCampaign, ServiceRequest


class ArtistImageForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ["name", "image"]


class AlbumCoverForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ["title", "artist", "genre", "cover_image", "release_date"]


class TrackAudioForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ["title", "album", "audio_file", "duration_seconds"]


class AdVideoForm(forms.ModelForm):
    class Meta:
        model = AdCampaign
        fields = ["name", "video", "starts_at", "ends_at"]


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ["email", "subject", "message"]
