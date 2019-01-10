"""Types and overall classes."""
import subprocess
from dataclasses import dataclass
from pathlib import PosixPath
from typing import Optional

import flickr_api
from loguru import logger


@dataclass
class FlickrPhoto:
    """Represent of a flickr photo.

    Locally and remotely.
    """

    flickr_id: str
    output_dir: PosixPath
    local_file: Optional[PosixPath] = None
    api_photo: flickr_api.objects.Photo = None

    def get_flickr_data(self) -> None:
        """Getting Photo informations from flickr."""
        logger.debug(f"getting flickr data for id: {self.flickr_id}")
        self.api_photo = flickr_api.Photo(id=self.flickr_id)

    @property
    def full_path(self) -> PosixPath:
        """Full local path."""
        if not self.api_photo:
            self.get_flickr_data()
        # pylint: disable=invalid-sequence-index
        secret = self.api_photo.getInfo()["secret"]
        return self.output_dir / f"{self.flickr_id}_{secret}_b.jpg"

    @property
    def exists_local(self) -> bool:
        """Check if local file exists."""
        return self.full_path.exists()

    def download(self) -> None:
        """Download image file from flickr."""
        if not self.local_file:
            self.local_file = self.full_path
        final_file = str(self.output_dir / self.local_file.stem)
        if not self.exists_local:
            logger.info(f"Download image: {self.flickr_id}")
            self.api_photo.save(final_file, size_label="Original")
        else:
            logger.info(f"{self.full_path} already exists!")

    def optimize(self) -> None:
        """Optimize file."""
        if not self.exists_local:
            logger.error(f"No local file found: {self.local_file}")
            return
        logger.info(f"Running optimisation on: {self.local_file}")
        subprocess.run(
            [
                "convert",
                str(self.full_path),
                "-resize",
                "960x>",
                "-strip",
                "-interlace",
                "Plane",
                "-quality",
                "85%",
                str(self.full_path),
            ]
        )

    @property
    def description(self) -> str:
        """Photo description."""
        if not self.api_photo:
            self.get_flickr_data()
        # pylint: disable=invalid-sequence-index
        return self.api_photo.getInfo()["title"]
