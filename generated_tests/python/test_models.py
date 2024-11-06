import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.http import HttpRequest
from mixer.backend.django import mixer
from .models import Band, Song
from .admin import DynOrderingBandAdmin, SongInlineDefaultOrdering, SongInlineNewOrdering

pytestmark = pytest.mark.django_db

class TestBandModel:
    def test_create_band(self):
        """
        Test normal creation of Band instances.
        """
        band = mixer.blend(Band, name="The Lorem Ipsums", bio="A band of placeholder text.", rank=1)
        assert band.name == "The Lorem Ipsums"
        assert band.bio == "A band of placeholder text."
        assert band.rank == 1
    
    def test_band_ordering(self):
        """
        Test the Meta class ordering of Band by name.
        """
        mixer.cycle(3).blend(Band, name=(name for name in ["Zeta", "Alpha", "Gamma"]))
        bands = list(Band.objects.all().values_list('name', flat=True))
        assert bands == ["Alpha", "Gamma", "Zeta"]

class TestSongModel:
    def test_create_song(self):
        """
        Test normal creation of Song instances.
        """
        band = mixer.blend(Band)
        song = mixer.blend(Song, band=band, name="Random Song", duration=300)
        assert song.band == band
        assert song.name == "Random Song"
        assert song.duration == 300

    def test_song_ordering(self):
        """
        Test the Meta class ordering of Song by name.
        """
        band = mixer.blend(Band)
        mixer.cycle(3).blend(Song, band=band, name=(name for name in ["Zeta", "Alpha", "Gamma"]))
        songs = list(Song.objects.all().values_list('name', flat=True))
        assert songs == ["Alpha", "Gamma", "Zeta"]

class TestDynOrderingBandAdmin:
    def setup_method(self):
        self.site = AdminSite()
        self.http_request = HttpRequest()
        self.http_request.user = mixer.blend(User, is_superuser=False)

    def test_dyn_ordering_non_superuser(self):
        """
        Test dynamic ordering for non-superuser request.
        """
        model_admin = DynOrderingBandAdmin(Band, self.site)
        self.assertEqual(model_admin.get_ordering(self.http_request), ["name"])

    def test_dyn_ordering_superuser(self):
        """
        Test dynamic ordering for superuser request.
        """
        self.http_request.user.is_superuser = True
        model_admin = DynOrderingBandAdmin(Band, self.site)
        self.assertEqual(model_admin.get_ordering(self.http_request), ["rank"])

class TestSongInlineOrdering:
    def test_default_ordering(self):
        """
        Test default ordering in SongInlineDefaultOrdering is not set.
        """
        assert SongInlineDefaultOrdering.ordering is None

    def test_new_ordering(self):
        """
        Test new ordering in SongInlineNewOrdering is set to duration.
        """
        assert SongInlineNewOrdering.ordering == ("duration",)
```