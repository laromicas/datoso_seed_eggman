"""Fetch and download DAT files."""

import json
import urllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from zipfile import ZipFile

from datoso.configuration.folder_helper import Folders
from datoso.helpers import Bcolors
from datoso.helpers.download import downloader
from datoso.helpers.file_utils import copy_path, move_path

from datoso_seed_eggman import __prefix__
from datoso_seed_eggman.classes import GithubDatRelease

folder_helper = Folders(seed=__prefix__)

def unzip_downloaded_files(release: GithubDatRelease) -> None:
    """Unzip downloaded files."""
    files = [release.file_from_link(link) for link in release.filtered_links() if link.endswith('.zip')]
    for file in files:
        if Path.exists(folder_helper.dats / file):
            if not Path.exists(folder_helper.dats / release.tag):
                Path(folder_helper.dats / release.tag).mkdir(parents=True, exist_ok=True)
            with ZipFile(folder_helper.dats / file) as zip_file:
                zip_file.extractall(folder_helper.dats / release.tag)


def download_dat(href: str, folder: Path) -> None:
    """Download a DAT file."""
    file_name = href.rsplit('/', maxsplit=1)[-1]
    destination = folder / file_name
    if file_name.endswith('.zip'):
        print(f'* Downloading {Bcolors.OKGREEN}{file_name}{Bcolors.ENDC} to {href}')
    downloader(url=href, destination=destination, reporthook=None)

def download_dats(links: list, folder: Path) -> None:
    """Create a thread for each download."""
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(download_dat, href, folder) for href in links
        ]
        for future in futures:
            future.result()


def backup_downloaded_files(files: list, folder_helper: Folders) -> None:
    """Backup downloaded files."""
    for file in files:
        file_name = file.rsplit('/', maxsplit=1)[-1]
        if file.endswith('.zip'):
            move_path(folder_helper.dats / file_name, folder_helper.backup)
        else:
            copy_path(folder_helper.dats / file_name, folder_helper.backup)

def get_folder_file(link: str) -> list:
    """Extract folder file from link."""
    return link.split('/')[-2:]


def fetch() -> None:
    """Fetch and download DAT files."""
    #Get all releases
    releases_url = 'https://api.github.com/repos/Eggmansworld/Datfiles/releases?per_page=100'
    repo_releases = {
        'teknoparrot': 'https://api.github.com/repos/Eggmansworld/TeknoParrot/releases/latest',
        'eggmans-arcade-repository': 'https://api.github.com/repos/Eggmansworld/Eggmans-Arcade-Repository/releases/latest',
    }
    response = urllib.request.urlopen(releases_url)
    releases = json.loads(response.read())
    all_releases = [GithubDatRelease.from_release(release) for release in releases]
    for tag, release in repo_releases.items():
        all_releases.append(GithubDatRelease.from_repo(tag, release))

    list_of_links = [release.filtered_links() for release in all_releases if len(release.filtered_links()) > 0]
    link_list = [item for sublist in list_of_links for item in sublist]

    folder_helper.clean_dats()
    folder_helper.create_all()
    download_dats(links=link_list, folder=folder_helper.dats)

    for release in all_releases:
        unzip_downloaded_files(release)

    backup_downloaded_files(files=link_list, folder_helper=folder_helper)
