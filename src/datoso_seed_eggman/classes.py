"""Classes script needed for Eggman Dats."""

from __future__ import annotations

import json
import urllib
from dataclasses import dataclass
from pathlib import Path

from datoso.configuration.folder_helper import Folders

from datoso_seed_eggman import __prefix__


@dataclass
class GithubDatRelease:
    """Temporal Docstring."""

    tag: str
    zip_links: list

    @staticmethod
    def from_release(release: dict) -> GithubDatRelease:
        """Create an EggmanRelease from a release."""
        tag = release['tag_name']
        zip_links = [asset['browser_download_url'] for asset in release['assets']]
        return GithubDatRelease(tag=tag, zip_links=zip_links)

    @staticmethod
    def from_repo(tag: str, release_url: str) -> GithubDatRelease:
        """Create an EggmanRelease from a release."""
        response = urllib.request.urlopen(release_url) #noqa: S310
        release = json.loads(response.read())

        zip_links = [asset['browser_download_url'] for asset in release['assets']]
        return GithubDatRelease(tag=tag, zip_links=zip_links)

    def file_from_link(self, link: str) -> str:
        """Return file name from link."""
        return link.rsplit('/', maxsplit=1)[-1]

    def filtered_links(self) -> list:
        """Return list of links not backup up yet."""
        folder_helper = Folders(seed=__prefix__)
        return [link for link in self.zip_links if not Path.exists(folder_helper.backup / self.file_from_link(link))]
