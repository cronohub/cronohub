import os
import logging
import sys
from collections import namedtuple
from github import Github, Repository
from multiprocessing import Pool
from pathlib import Path
from subprocess import run, CalledProcessError
from urllib.request import urlretrieve
from typing import List


logging.basicConfig(filename='cronohub.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger('cronohub_logger')
Repourl = namedtuple('Repourl', ['url', 'name'])

def get_repo_list() -> List[Repository.Repository]:
    """
    Gather a list of remote forks for a given user.
    Only repositories are selected for which the given user is an owner.
    This prevents the inclusion of Company based forks.

    :return: List[Repository.Repository]
        A list of remote forks for the current user.
    """
    g = Github(os.environ['FSYNC_GITHUB_TOKEN'])
    repos = []
    user = g.get_user()
    for repo in user.get_repos(type="owner"):
        if not repo.fork:
            repos.append(repo)
    return repos

def gather_archive_urls(repos: List[Repository.Repository]) -> List[Repourl]:
    """
    Gather a list of URLs for the repositories.
    """
    return list(map(lambda r: Repourl(url=r.get_archive_link(archive_format="zipball"), name=r.name), repos))

def download(repo_url):
    """
    Download a single URL. This is used by `download_urls` as the function
    to map to.
    """
    url, name = repo_url
    base = os.getcwd()
    target = Path.joinpath(base, "target", name + ".zip")
    urlretrieve(url, target)

def download_urls(urls: List[str]):
    """
    Multithreaded url downloader.
    """
    base = os.getcwd()
    target = Path.joinpath(base, "target")
    if not os.path.exists(target):
        os.makedirs(target)
    with Pool(5) as p:
        p.map(download, urls)

def main():
    """
    The main of cronohub. Gathers the list of repositories to archive
    and filters them based on a `.repos_list` file that can be located
    under `~/.config/fsyncer/.repo_list`. This file contains a list
    of repository names which the user wishes to syncronize. Anything else
    will be ignored.
    :return: None
    """
    print(r'''
	_______  ______    _______  __    _  _______  __   __  __   __  _______
	|       ||    _ |  |       ||  |  | ||       ||  | |  ||  | |  ||  _    |
	|       ||   | ||  |   _   ||   |_| ||   _   ||  |_|  ||  | |  || |_|   |
	|       ||   |_||_ |  | |  ||       ||  | |  ||       ||  |_|  ||       |
	|      _||    __  ||  |_|  ||  _    ||  |_|  ||       ||       ||  _   |
	|     |_ |   |  | ||       || | |   ||       ||   _   ||       || |_|   |
	|_______||___|  |_||_______||_|  |__||_______||__| |__||_______||_______|

    Beginning archiving...
    ''')

    if "CRONO_GITHUB_TOKEN" not in os.environ:
        print("Please set up a token by CRONO_GITHUB_TOKEN=<token>.")
        sys.exit(1)

    repo_list = Path(os.path.join(Path.home(), '.config', 'cronohub', '.repo_list'))
    only = []
    if repo_list.is_file():
        logger.info('found configuration file... syncing repos from file')
        with open(repo_list) as conf:
            for line in conf:
                only.append(line.strip())

    logger.info('retrieving repositories for user')
    repos = get_repo_list()
    if len(only) > 0:
        repos = list(filter(lambda r: r.name in only, repos))

    logger.info('Gathering urls for %d repositories.' % len(repos))
    urls = gather_archive_urls(repos)
    logger.info('Downloading archives.')
    download_urls(urls)
