import io
import os
import random
from pathlib import Path
from urllib.parse import urlencode

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from faker import Faker
import requests

from app.models import Genre, Artist, Album, Track, AdCampaign, ServiceRequest


class Command(BaseCommand):
    help = "Generate fake data for development: genres, artists, albums, tracks, users, ad campaigns, and service requests."

    def add_arguments(self, parser):
        parser.add_argument('--genres', type=int, default=10)
        parser.add_argument('--artists', type=int, default=20)
        parser.add_argument('--albums', type=int, default=30)
        parser.add_argument('--tracks', type=int, default=100)
        parser.add_argument('--users', type=int, default=15)
        parser.add_argument('--ad_campaigns', type=int, default=10)
        parser.add_argument('--service_requests', type=int, default=5)

    def handle(self, *args, **options):
        fake = Faker()
        rng = random.Random(42)

        gcount = options['genres']
        acount = options['artists']
        albcount = options['albums']
        tcount = options['tracks']
        ucount = options['users']
        adcount = options['ad_campaigns']
        srcount = options['service_requests']

        # Genres
        genres = []
        for _ in range(gcount):
            name = fake.unique.word().title()
            genres.append(Genre.objects.get_or_create(name=name)[0])
        self.stdout.write(self.style.SUCCESS(f"Genres: {len(genres)}"))

        # Artists
        artists = []
        for _ in range(acount):
            a = Artist(name=fake.unique.name())
            img_bytes = self._fetch_placeholder_image(query='musician')
            if img_bytes:
                a.image.save(f"{fake.uuid4()}.jpg", ContentFile(img_bytes), save=False)
            a.save()
            artists.append(a)
        self.stdout.write(self.style.SUCCESS(f"Artists: {len(artists)}"))

        # Albums
        albums = []
        for _ in range(albcount):
            artist = rng.choice(artists)
            genre = rng.choice(genres) if genres else None
            al = Album(title=fake.sentence(nb_words=3).rstrip('.'), artist=artist, genre=genre)
            img_bytes = self._fetch_placeholder_image(query='album cover')
            if img_bytes:
                al.cover_image.save(f"{fake.uuid4()}.jpg", ContentFile(img_bytes), save=False)
            al.save()
            albums.append(al)
        self.stdout.write(self.style.SUCCESS(f"Albums: {len(albums)}"))

        # Tracks
        tracks = []
        for _ in range(tcount):
            album = rng.choice(albums) if albums else None
            if not album:
                break
            tr = Track(title=fake.sentence(nb_words=2).rstrip('.'), album=album, duration_seconds=rng.randint(90, 360))
            # Create a tiny fake audio file (silence placeholder) as bytes
            audio_bytes = self._fake_audio_wav_silence(duration_sec=1)
            tr.audio_file.save(f"{fake.uuid4()}.wav", ContentFile(audio_bytes), save=False)
            tr.save()
            tracks.append(tr)
        self.stdout.write(self.style.SUCCESS(f"Tracks: {len(tracks)}"))

        # Users
        User = get_user_model()
        for _ in range(ucount):
            email = fake.unique.email()
            if not User.objects.filter(username=email).exists():
                User.objects.create_user(username=email, email=email, password='password123')
        self.stdout.write(self.style.SUCCESS(f"Users total: {User.objects.count()}"))

        # Ad Campaigns
        ads = []
        for _ in range(adcount):
            ad = AdCampaign(name=fake.catch_phrase())
            # Attach a small placeholder MP4 via remote fetch or local dummy bytes
            video_bytes = self._fetch_placeholder_video()
            if video_bytes:
                ad.video.save(f"{fake.uuid4()}.mp4", ContentFile(video_bytes), save=False)
            ad.save()
            ads.append(ad)
        self.stdout.write(self.style.SUCCESS(f"AdCampaigns: {len(ads)}"))

        # Service Requests
        for _ in range(srcount):
            ServiceRequest.objects.create(
                email=fake.email(),
                subject=fake.sentence(nb_words=6).rstrip('.'),
                message=fake.paragraph(nb_sentences=3),
            )
        self.stdout.write(self.style.SUCCESS(f"ServiceRequests total: {ServiceRequest.objects.count()}"))

    def _fetch_placeholder_image(self, query: str = 'music') -> bytes | None:
        # Prefer Pexels API if available
        api_key = getattr(settings, 'PEXELS_API_KEY', None)
        try:
            if api_key:
                headers = {"Authorization": api_key}
                params = {"query": query, "per_page": 1, "orientation": "landscape"}
                resp = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=10)
                if resp.ok:
                    data = resp.json()
                    photos = data.get('photos') or []
                    if photos:
                        url = photos[0]['src']['medium']
                        img = requests.get(url, timeout=10)
                        if img.ok:
                            return img.content
            # Fallback: Unsplash source (no key) or placeholder image service
            url = f"https://source.unsplash.com/400x300/?{requests.utils.quote(query)}"
            img = requests.get(url, timeout=10)
            if img.ok:
                return img.content
        except Exception:
            return None
        return None

    def _fetch_placeholder_video(self) -> bytes | None:
        # Try to fetch a small mp4 sample; fallback to minimal mp4 header bytes that most players won't play
        try:
            # Sample small mp4 from file-examples
            url = "https://file-examples.com/storage/fe9b9f71f3a8a8e0e0c1b5a/2017/04/file_example_MP4_480_1_5MG.mp4"
            r = requests.get(url, timeout=15)
            if r.ok and len(r.content) > 0:
                return r.content
        except Exception:
            pass
        # Fallback tiny bytes
        return b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42mp41"

    def _fake_audio_wav_silence(self, duration_sec: int = 1) -> bytes:
        # Produce a minimal WAV header with silence PCM 8kHz mono 16-bit
        import wave
        import struct
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as w:
            sample_rate = 8000
            w.setnchannels(1)
            w.setsampwidth(2)  # 16-bit
            w.setframerate(sample_rate)
            frames = duration_sec * sample_rate
            silence = (0,) * frames
            w.writeframes(b''.join(struct.pack('<h', s) for s in silence))
        return buf.getvalue()
