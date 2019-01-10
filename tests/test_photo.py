# pylint: disable=missing-docstring,redefined-outer-name
from pathlib import Path
from unittest.mock import PropertyMock, patch

from flickr2pelican import photo


@patch("flickr2pelican.photo.flickr_api")
def test_full_path(mock_flickr_api, tmpdir):
    mock_flickr_api.Photo.return_value.getInfo.return_value = {"secret": "s3cr37"}
    flickr_photo = photo.FlickrPhoto("abc123", tmpdir)

    assert flickr_photo.full_path == tmpdir / f"abc123_s3cr37_b.jpg"


@patch("flickr2pelican.photo.flickr_api")
def test_download(mock_flickr_api, tmpdir):
    mock_flickr_api.Photo.return_value.getInfo.return_value = {"secret": "s3cr37"}
    flickr_photo = photo.FlickrPhoto("abc123", Path(tmpdir.strpath))
    flickr_photo.download()

    mock_flickr_api.Photo.return_value.save.assert_called_with(
        tmpdir.join("abc123_s3cr37_b").strpath, size_label="Original"
    )


@patch("flickr2pelican.photo.logger")
@patch("flickr2pelican.photo.FlickrPhoto.exists_local", new_callable=PropertyMock)
@patch("flickr2pelican.photo.flickr_api")
def test_download_file_exists(mock_flickr_api, mock_exists_local, mock_logger, tmpdir):
    mock_exists_local.return_value = True
    mock_flickr_api.Photo.return_value.getInfo.return_value = {"secret": "s3cr37"}
    flickr_photo = photo.FlickrPhoto("abc123", Path(tmpdir.strpath))
    flickr_photo.download()

    mock_flickr_api.Photo.return_value.save.assert_not_called()

    mock_logger.info.assert_called_with(
        f"{tmpdir.strpath}/abc123_s3cr37_b.jpg already exists!"
    )


@patch("flickr2pelican.photo.subprocess")
@patch("flickr2pelican.photo.FlickrPhoto.exists_local", new_callable=PropertyMock)
@patch("flickr2pelican.photo.flickr_api")
def test_optimize(mock_flickr_api, mock_exists_local, mock_subprocess, tmpdir):
    mock_exists_local.return_value = True
    mock_flickr_api.Photo.return_value.getInfo.return_value = {"secret": "s3cr37"}
    flickr_photo = photo.FlickrPhoto("abc123", Path(tmpdir.strpath))
    flickr_photo.optimize()

    mock_subprocess.run.assert_called_with(
        [
            "convert",
            tmpdir.join(f"abc123_s3cr37_b.jpg").strpath,
            "-resize",
            "960x>",
            "-strip",
            "-interlace",
            "Plane",
            "-quality",
            "85%",
            tmpdir.join(f"abc123_s3cr37_b.jpg").strpath,
        ]
    )


@patch("flickr2pelican.photo.subprocess")
@patch("flickr2pelican.photo.logger")
@patch("flickr2pelican.photo.FlickrPhoto.exists_local", new_callable=PropertyMock)
def test_optimize_file_not_found(
    mock_exists_local, mock_logger, mock_subprocess, tmpdir
):
    mock_exists_local.return_value = False
    flickr_photo = photo.FlickrPhoto("abc123", Path(tmpdir.strpath))

    flickr_photo.optimize()
    mock_logger.error.assert_called_with("No local file found: None")
