# pylint: disable=missing-docstring,redefined-outer-name
import http
from pathlib import Path
from unittest.mock import Mock, PropertyMock, call, patch

from flickr2pelican import photo


def test_full_path(tmpdir):
    mock_flickr_mod = Mock()
    mock_flickr_mod.Photo.return_value.getInfo.return_value = {"secret": "s3cr37"}
    flickr_photo = photo.FlickrPhoto("abc123", tmpdir, mock_flickr_mod)

    assert flickr_photo.full_path == tmpdir / f"abc123_s3cr37_b.jpg"


def test_download(tmpdir):
    mock_flickr_mod = Mock()
    mock_flickr_mod.Photo.return_value.getInfo.return_value = {"secret": "s3cr37"}
    flickr_photo = photo.FlickrPhoto("abc123", Path(tmpdir.strpath), mock_flickr_mod)

    assert flickr_photo.downloaded is False

    flickr_photo.download()

    mock_flickr_mod.Photo.return_value.save.assert_called_with(
        tmpdir.join("abc123_s3cr37_b").strpath, size_label="Original"
    )

    assert flickr_photo.downloaded is True


@patch("flickr2pelican.photo.logger")
@patch("flickr2pelican.photo.FlickrPhoto.exists_local", new_callable=PropertyMock)
def test_download_file_exists(mock_exists_local, mock_logger, tmpdir):
    mock_exists_local.return_value = True
    mock_flickr_mod = Mock()
    mock_flickr_mod.Photo.return_value.getInfo.return_value = {"secret": "s3cr37"}
    flickr_photo = photo.FlickrPhoto("abc123", Path(tmpdir.strpath), mock_flickr_mod)
    flickr_photo.download()

    mock_flickr_mod.Photo.return_value.save.assert_not_called()

    mock_logger.info.assert_called_with(
        f"{tmpdir.strpath}/abc123_s3cr37_b.jpg already exists!"
    )


@patch("flickr2pelican.photo.logger")
@patch("flickr2pelican.photo.FlickrPhoto.exists_local", new_callable=PropertyMock)
def test_download_incomplete_read(mock_exists_local, mock_logger, tmpdir):
    mock_exists_local.return_value = False
    mock_flickr_mod = Mock()
    mock_flickr_mod.Photo.return_value.save.side_effect = [
        http.client.IncompleteRead("foo bar"),
        True,
    ]
    mock_flickr_mod.Photo.return_value.getInfo.return_value = {"secret": "s3cr37"}
    Path(tmpdir.join("abc123_s3cr37_b.jpg").strpath).touch()
    flickr_photo = photo.FlickrPhoto("abc123", Path(tmpdir.strpath), mock_flickr_mod)

    flickr_photo.download()

    mock_flickr_mod.Photo.return_value.save.assert_has_calls(
        [
            call(tmpdir.join("abc123_s3cr37_b").strpath, size_label="Original"),
            call(tmpdir.join("abc123_s3cr37_b").strpath, size_label="Original"),
        ]
    )

    mock_logger.error.assert_has_calls([call("incomplete download. will try again...")])

    mock_logger.debug.assert_has_calls(
        [
            call("getting flickr data for id: abc123"),
            call("removed {}".format(tmpdir.join("abc123_s3cr37_b.jpg").strpath)),
            call("raised counter to 1"),
        ]
    )


@patch("flickr2pelican.photo.logger")
@patch("flickr2pelican.photo.FlickrPhoto.exists_local", new_callable=PropertyMock)
def test_download_exception(mock_exists_local, mock_logger, tmpdir):
    mock_exists_local.return_value = False
    mock_flickr_mod = Mock()
    mock_flickr_mod.Photo.return_value.save.side_effect = [KeyError("foo bar"), True]
    mock_flickr_mod.Photo.return_value.getInfo.return_value = {"secret": "s3cr37"}
    Path(tmpdir.join("abc123_s3cr37_b.jpg").strpath).touch()
    flickr_photo = photo.FlickrPhoto("abc123", Path(tmpdir.strpath), mock_flickr_mod)

    flickr_photo.download()

    mock_flickr_mod.Photo.return_value.save.assert_has_calls(
        [
            call(tmpdir.join("abc123_s3cr37_b").strpath, size_label="Original"),
            call(tmpdir.join("abc123_s3cr37_b").strpath, size_label="Original"),
        ]
    )

    mock_logger.error.assert_called_with("catched error. will try again...")


@patch("flickr2pelican.photo.FlickrPhoto.api_photo", new_callable=PropertyMock)
@patch("flickr2pelican.photo.FlickrPhoto.local_file", new_callable=PropertyMock)
@patch("flickr2pelican.photo.logger")
def test_download_exception_in_exception(
    mock_logger, mock_local_file, mock_api_photo, tmpdir
):
    test_image = Path(tmpdir.join("foo_bar.jpg").strpath)
    mock_local_file.return_value = test_image
    mock_api_photo.return_value.save.side_effect = [KeyError("foo bar"), True]
    flickr_photo = photo.FlickrPhoto("abc124", Path(tmpdir.strpath), Mock())
    flickr_photo.download()

    mock_logger.exception.assert_has_calls = [
        call(KeyError("foo bar")),
        call(FileNotFoundError(2, "No such file or directory")),
    ]

    mock_logger.error.assert_has_calls = [call("catched error. will try again...")]

    mock_logger.info.assert_has_calls = [
        call(f"Download image: abc123 to {test_image}"),
        call(f"Download image: abc123 to {test_image}"),
    ]


@patch("flickr2pelican.photo.subprocess")
@patch("flickr2pelican.photo.FlickrPhoto.exists_local", new_callable=PropertyMock)
def test_optimize(mock_exists_local, mock_subprocess, tmpdir):
    mock_exists_local.return_value = True
    mock_flickr_mod = Mock()
    mock_flickr_mod.Photo.return_value.getInfo.return_value = {"secret": "s3cr37"}
    flickr_photo = photo.FlickrPhoto("abc123", Path(tmpdir.strpath), mock_flickr_mod)
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


@patch("flickr2pelican.photo.logger")
@patch("flickr2pelican.photo.FlickrPhoto.exists_local", new_callable=PropertyMock)
def test_optimize_file_not_found(mock_exists_local, mock_logger, tmpdir):
    mock_exists_local.return_value = False
    flickr_photo = photo.FlickrPhoto("abc123", Path(tmpdir.strpath), Mock())

    flickr_photo.optimize()
    mock_logger.error.assert_called_with("No local file found: None")


def test_description(tmpdir):
    mock_flickr_mod = Mock()
    mock_flickr_mod.Photo.return_value.getInfo.return_value = {"title": "my photo"}
    flickr_photo = photo.FlickrPhoto("abc123", Path(tmpdir.strpath), mock_flickr_mod)

    assert flickr_photo.description == "my photo"


@patch("flickr2pelican.photo.FlickrPhoto.full_path", new_callable=PropertyMock)
@patch("flickr2pelican.photo.FlickrPhoto.description", new_callable=PropertyMock)
def test_markdown(
    mock_description, mock_full_path, tmpdir
):  # pylint: disable=unused-argument
    mock_description.return_value = "this is a description"
    mock_full_path.return_value = Path(tmpdir.join("foo_bar.jpg").strpath)
    flickr_photo = photo.FlickrPhoto("abc123", Path(tmpdir.strpath), Mock())

    assert (
        flickr_photo.markdown == "![this is a description]({static}/images/foo_bar.jpg)"
    )
