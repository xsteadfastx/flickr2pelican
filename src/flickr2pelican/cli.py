"""Console script for flickr2pelican"""
from pathlib import Path

import click
import flickr_api
from loguru import logger

from flickr2pelican import core


@click.command()
@click.option("-u", "--username", help="flickr username", type=click.types.STRING)
@click.option(
    "-l",
    "--local-dir",
    help="local directory to download images to",
    type=click.types.Path(exists=True),
)
@click.option("-k", "--key", help="flickr api key", type=click.types.STRING)
@click.option("-s", "--secret", help="flickr api secret", type=click.types.STRING)
@click.argument("number", type=click.types.INT)
def main(username: str, local_dir: str, key: str, secret: str, number: int) -> None:
    """Downloads flickr images, optimizes them and creates markdown code"""
    print("YYYYYEAH")
    try:
        # pylint: disable=import-error
        import pelicanconf

        if not username and hasattr(pelicanconf, "FLICKR_USERNAME"):
            logger.debug(f"uses username: {pelicanconf.FLICKR_USERNAME}")
            username = pelicanconf.FLICKR_USERNAME

        if not local_dir and hasattr(pelicanconf, "FLICKR_IMAGE_PATH"):
            logger.debug(f"uses local_dir: {pelicanconf.FLICKR_IMAGE_PATH}")
            local_dir = pelicanconf.FLICKR_IMAGE_PATH

        if not key and hasattr(pelicanconf, "FLICKR_API_KEY"):
            logger.debug(f"uses key: {pelicanconf.FLICKR_API_KEY}")
            key = pelicanconf.FLICKR_API_KEY

        if not secret and hasattr(pelicanconf, "FLICKR_API_SECRET"):
            logger.debug(f"uses secret: {pelicanconf.FLICKR_API_SECRET}")
            secret = pelicanconf.FLICKR_API_SECRET

    except ModuleNotFoundError:
        pass

    if not username:
        username = click.prompt("flickr username")

    if not local_dir:
        local_dir = click.prompt("local dir")

    if not key:
        key = click.prompt("flickr api key")

    if not secret:
        secret = click.prompt("flickr api secret")

    flickr_api.set_keys(api_key=key, api_secret=secret)

    flickr_user = core.get_user(username, flickr_api)
    photos = core.get_latest_photos(flickr_user, number, Path(local_dir), flickr_api)
    core.download_n_optimize(photos)
    markdowns = [i.markdown for i in photos]

    click.secho("---BEGIN MARKDOWN---\n", bold=True)
    click.echo("\n\n".join(markdowns))
    click.secho("\n---END MARKDOWN---", bold=True)
