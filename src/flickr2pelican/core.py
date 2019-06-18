"""Core module."""
from pathlib import Path
from typing import List

import flickr_api
from loguru import logger

from flickr2pelican.photo import FlickrPhoto


def get_user(username: str, flickr_mod: flickr_api) -> flickr_api.objects.Person:
    """Get flickr user."""
    user = flickr_mod.Person.findByUserName(username)
    logger.debug(f"got user {user}")
    return user


def get_latest_photos(
    user: flickr_api.objects.Person,
    number: int,
    image_folder: Path,
    flickr_mod: flickr_api,
) -> List[FlickrPhoto]:
    """Get latest number of photos from the flickr API."""
    photos = []
    for photo in user.getPublicPhotos()[0:number]:
        logger.debug(f"adding {photo} to list")
        photos.append(FlickrPhoto(photo.id, image_folder, flickr_mod, api_photo=photo))
    return photos


def download_n_optimize(photos: List[FlickrPhoto]) -> None:
    """Downloads and optimizes images."""
    for photo in photos:
        logger.info("downloading...")
        photo.download()
        if photo.downloaded:
            logger.info("optimizing...")
            photo.optimize()
