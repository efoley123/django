import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase
from mixer.backend.django import mixer
from unittest.mock import patch

from your_app.models import Band, Song
from your_app.admin import DynOrderingBandAdmin, SongInlineDefaultOrdering, SongInlineNewOrdering

pytestmark = pytest.mark.django_db

class TestBandModel:
    def test_create_band(self):
        """
        Test normal case for creating a Band instance.
        """
        band = mixer.blend(Band, name="Nirvana", bio="Grunge band", rank=1)
        assert band.name == "Nirvana"
        assert band.bio == "Grunge band"
        assert band.rank == 1

    def test_band_ordering(self):
        """
        Test the Meta class ordering of Band model.
        """
        band1 = mixer.blend(Band, name="Zebra")
        band2 = mixer.blend(Band, name="Armadillo")
        bands = Band.objects.all()
        assert bands[0].name == "Armadillo"
        assert bands[1].name == "Zebra"

class TestSongModel:
    def test_create_song(self):
        """
        Test normal case for creating a Song instance.
        """
        band = mixer.blend(Band)
        song = mixer.blend(Song, band=band, name="Smells Like Teen Spirit", duration=300)
        assert song.band == band
        assert song.name == "Smells Like Teen Spirit"
        assert song.duration == 300

    def test_song_ordering(self):
        """
        Test the Meta class ordering of Song model.
        """
        band = mixer.blend(Band)
        song1 = mixer.blend(Song, name="Zephyr Song", band=band)
        song2 = mixer.blend(Song, name="Californication", band=band)
        songs = Song.objects.all()
        assert songs[0].name == "Californication"
        assert songs[1].name == "Zephyr Song"

class TestDynOrderingBandAdmin:
    def test_superuser_ordering(self, rf):
        """
        Test the get_ordering method for a superuser request.
        """
        site = AdminSite()
        admin = DynOrderingBandAdmin(Band, site)
        request = rf.get('/')
        request.user = mixer.blend(User, is_superuser=True)
        ordering = admin.get_ordering(request)
        assert ordering == ["rank"]

    def test_regular_user_ordering(self, rf):
        """
        Test the get_ordering method for a regular user request.
        """
        site = AdminSite()
        admin = DynOrderingBandAdmin(Band, site)
        request = rf.get('/')
        request.user = mixer.blend(User, is_superuser=False)
        ordering = admin.get_ordering(request)
        assert ordering == ["name"]

@pytest.fixture
def band_and_songs(db):
    band = mixer.blend(Band)
    song1 = mixer.blend(Song, band=band, name="Learn to Fly")
    song2 = mixer.blend(Song, band=band, name="Everlong")
    return band, [song1, song2]

class TestSongInlineOrdering:
    def test_default_ordering(self, band_and_songs):
        """
        Test that SongInlineDefaultOrdering has no custom ordering.
        """
        inline = SongInlineDefaultOrdering(Band, AdminSite())
        assert inline.get_ordering(None) is None

    def test_new_ordering(self, band_and_songs):
        """
        Test that SongInlineNewOrdering uses duration for ordering.
        """
        inline = SongInlineNewOrdering(Band, AdminSite())
        assert inline.ordering == ("duration",)