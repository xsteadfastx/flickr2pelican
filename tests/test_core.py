# pylint: disable=missing-docstring
from pathlib import Path
from unittest.mock import Mock, patch, sentinel

from flickr2pelican import core
from flickr2pelican.photo import FlickrPhoto


@patch("flickr2pelican.core.logger")
@patch("flickr2pelican.core.flickr_api")
def test_get_user(mock_flickr_api, mock_logger):
    mock_flickr_api.Person.findByUserName.return_value = sentinel.user
    assert core.get_user("foobar") == sentinel.user
    mock_logger.debug.assert_called_with("got user sentinel.user")


def test_get_latest_photos(tmpdir):
    mock_user = Mock()
    test_photo = sentinel.photo
    sentinel.photo.id = 777
    mock_user.getPublicPhotos.return_value = [test_photo]

    assert core.get_latest_photos(mock_user, 1, Path(tmpdir.strpath)) == [
        FlickrPhoto(
            flickr_id=777,
            output_dir=Path(tmpdir.strpath),
            local_file=None,
            api_photo=sentinel.photo,
            downloaded=False,
        )
    ]


@patch("flickr2pelican.core.FlickrPhoto.optimize")
@patch("flickr2pelican.core.FlickrPhoto.download")
def test_download_n_optimize(mock_download, mock_optimize, tmpdir):
    photos = [
        FlickrPhoto(
            flickr_id=777,
            output_dir=Path(tmpdir.strpath),
            local_file=None,
            api_photo=sentinel.photo,
            downloaded=True,
        )
    ]

    core.download_n_optimize(photos)

    mock_download.assert_called()
    mock_optimize.assert_called()
