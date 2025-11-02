from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import (
    ArtistImageForm,
    AlbumCoverForm,
    TrackAudioForm,
    AdVideoForm,
    ServiceRequestForm,
)
from .models import Artist, Album, Track, AdCampaign


def home(request):
    context = {
        "artists": Artist.objects.all()[:10],
        "albums": Album.objects.select_related("artist").all()[:10],
        "tracks": Track.objects.select_related("album", "album__artist").all()[:10],
        "ads": AdCampaign.objects.all()[:10],
    }
    return render(request, "home.html", context)


def upload_success(request):
    return render(request, "success.html")


def upload_artist_image(request):
    if request.method == "POST":
        form = ArtistImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse("upload_success"))
    else:
        form = ArtistImageForm()
    return render(request, "upload_artist.html", {"form": form})


def upload_album_cover(request):
    if request.method == "POST":
        form = AlbumCoverForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse("upload_success"))
    else:
        form = AlbumCoverForm()
    return render(request, "upload_album.html", {"form": form})


def upload_track_audio(request):
    if request.method == "POST":
        form = TrackAudioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse("upload_success"))
    else:
        form = TrackAudioForm()
    return render(request, "upload_track.html", {"form": form})


def upload_ad_video(request):
    if request.method == "POST":
        form = AdVideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse("upload_success"))
    else:
        form = AdVideoForm()
    return render(request, "upload_ad.html", {"form": form})


def service_request(request):
    if request.method == "POST":
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            sr = form.save()
            # send email to developer (console backend in dev)
            send_mail(
                subject=f"Service Request: {sr.subject}",
                message=f"From: {sr.email}\n\n{sr.message}",
                from_email=sr.email,
                recipient_list=[getattr(settings, "DEVELOPER_EMAIL", "developer@tfnms.co")],
                fail_silently=True,
            )
            return redirect(reverse("upload_success"))
    else:
        form = ServiceRequestForm()
    return render(request, "service_request.html", {"form": form})
