import pytest
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from your_app.models import Band, Song
from your_app.admin import DynOrderingBandAdmin, SongInlineDefaultOrdering, SongInlineNewOrdering
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest

pytestmark = pytest.mark.django_db

class TestBand:
    def test_band_creation(self):
        """
        Ensure we can create a Band instance.
        """
        band = mixer.blend(Band, name="Test Band", bio="Test Bio", rank=1)
        assert band.name == "Test Band", "Should create a band with a name"
        assert band.bio == "Test Bio", "Should create a band with a bio"
        assert band.rank == 1, "Should create a band with a rank"

    def test_band_ordering(self):
        """
        Ensure Band instances are ordered correctly.
        """
        mixer.blend(Band, name="Band Z")
        mixer.blend(Band, name="Band A")
        bands = Band.objects.all()
        assert bands[0].name == "Band A", "Should be ordered by name ascending"

class TestSong:
    def test_song_creation(self):
        """
        Ensure we can create a Song instance.
        """
        band = mixer.blend(Band)
        song = mixer.blend(Song, name="Test Song", duration=320, band=band)
        assert song.name == "Test Song", "Should create a song with a name"
        assert song.duration == 320, "Should create a song with a duration"
        assert song.band == band, "Should associate the song with a band"

    def test_song_ordering(self):
        """
        Ensure Song instances are ordered correctly.
        """
        band = mixer.blend(Band)
        mixer.blend(Song, name="Song Z", band=band)
        mixer.blend(Song, name="Song A", band=band)
        songs = Song.objects.all()
        assert songs[0].name == "Song A", "Should be ordered by name ascending"

class TestAdmin:
    @pytest.fixture
    def superuser_request(self):
        request = HttpRequest()
        request.user = mixer.blend(User, is_superuser=True)
        return request

    @pytest.fixture
    def regular_user_request(self):
        request = HttpRequest()
        request.user = mixer.blend(User, is_superuser=False)
        return request

    def test_dyn_ordering_band_admin_superuser(self, superuser_request):
        """
        Ensure superuser sees Bands ordered by rank.
        """
        site = AdminSite()
        admin = DynOrderingBandAdmin(Band, site)
        ordering = admin.get_ordering(superuser_request)
        assert ordering == ["rank"], "Superuser should see bands ordered by rank"

    def test_dyn_ordering_band_admin_regular_user(self, regular_user_request):
        """
        Ensure regular user sees Bands ordered by name.
        """
        site = AdminSite()
        admin = DynOrderingBandAdmin(Band, site)
        ordering = admin.get_ordering(regular_user_request)
        assert ordering == ["name"], "Regular user should see bands ordered by name"

class TestSongInlineOrdering:
    def test_song_inline_default_ordering(self):
        """
        Ensure SongInlineDefaultOrdering has no custom ordering.
        """
        inline = SongInlineDefaultOrdering(Band, AdminSite())
        assert inline.get_ordering(None) is None, "Default ordering should be None"

    def test_song_inline_new_ordering(self):
        """
        Ensure SongInlineNewOrdering uses duration for ordering.
        """
        inline = SongInlineNewOrdering(Band, AdminSite())
        assert inline.ordering == ("duration",), "Should be ordered by duration"