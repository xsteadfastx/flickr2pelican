# pylint: disable=missing-docstring
from pathlib import Path
from unittest.mock import Mock, patch, sentinel

from flickr2pelican import core
from flickr2pelican.photo import FlickrPhoto


@patch("flickr2pelican.core.logger")
def test_get_user(mock_logger):
    mock_flickr_mod = Mock()
    mock_flickr_mod.Person.findByUserName.return_value = sentinel.user
    assert core.get_user("foobar", mock_flickr_mod) == sentinel.user
    mock_logger.debug.assert_called_with("got user sentinel.user")


def test_get_latest_photos(tmpdir):
    mock_user = Mock()
    mock_flickr_mod = Mock()
    test_photo = sentinel.photo
    sentinel.photo.id = 777
    mock_user.getPublicPhotos.return_value = [test_photo]

    assert core.get_latest_photos(
        mock_user, 1, Path(tmpdir.strpath), mock_flickr_mod
    ) == [
        FlickrPhoto(
            flickr_id=777,
            output_dir=Path(tmpdir.strpath),
            local_file=None,
            api_photo=sentinel.photo,
            downloaded=False,
            flickr_mod=mock_flickr_mod,
        )
    ]


@patch("flickr2pelican.core.FlickrPhoto.optimize")
@patch("flickr2pelican.core.FlickrPhoto.download")
def test_download_n_optimize(mock_download, mock_optimize, tmpdir):
    mock_flickr_mod = Mock()
    photos = [
        FlickrPhoto(
            flickr_id=777,
            output_dir=Path(tmpdir.strpath),
            local_file=None,
            api_photo=sentinel.photo,
            downloaded=True,
            flickr_mod=mock_flickr_mod,
        )
    ]

    core.download_n_optimize(photos)

    mock_download.assert_called()
    mock_optimize.assert_called()
