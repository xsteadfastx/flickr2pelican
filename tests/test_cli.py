# pylint: disable=missing-docstring,redefined-outer-name
from pathlib import Path
from unittest.mock import Mock, call, patch, sentinel

from flickr2pelican import cli


@patch("flickr2pelican.cli.logger")
@patch("flickr2pelican.cli.core")
def test_main_pelicanconf(
    mock_core, mock_logger, runner, tmpdir
):  # pylint: disable=unused-argument
    mock_pelicanconf = Mock()
    mock_pelicanconf.FLICKR_USERNAME = "foobar"
    mock_pelicanconf.FLICKR_IMAGE_PATH = tmpdir.strpath

    with patch.dict("sys.modules", pelicanconf=mock_pelicanconf):
        result = runner.invoke(cli.main, ["10"])

    assert mock_logger.debug.call_args_list == [
        call("uses username: foobar"),
        call(f"uses local_dir: {tmpdir.strpath}"),
    ]
    assert result.exit_code == 0


@patch("flickr2pelican.cli.core")
@patch("flickr2pelican.cli.click.prompt")
@patch("flickr2pelican.cli.click.echo")
def test_main_prompt(mock_echo, mock_prompt, mock_core, runner, tmpdir):
    mock_prompt.side_effect = ["barfoo", tmpdir.strpath]
    mock_core.get_user.return_value = sentinel.flickr_user
    test_photo = sentinel.foto
    test_photo.markdown = "foo"
    mock_photos = [test_photo]
    mock_core.get_latest_photos.return_value = mock_photos

    result = runner.invoke(cli.main, ["10"], catch_exceptions=False)

    assert result.exit_code == 0
    mock_prompt.assert_has_calls([call("flickr username"), call("local dir")])
    mock_core.get_user.assert_called_with("barfoo")
    mock_core.get_latest_photos.assert_called_with(
        sentinel.flickr_user, 10, Path(tmpdir.strpath)
    )
    mock_core.download_n_optimize.assert_called_with(mock_photos)

    mock_echo.assert_has_calls([call("foo")])
