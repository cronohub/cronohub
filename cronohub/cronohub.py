import argparse
import logging
import os
import time
import sys
from collections import namedtuple
from importlib import import_module
from multiprocessing import Pool
from pathlib import Path
from typing import List
from urllib.request import urlretrieve

import pkg_resources
from colored import attr, bg, fg
from github import Github, Repository

logging.basicConfig(filename='cronohub.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger('cronohub_logger')
Repourl = namedtuple('Repourl', ['url', 'name'])
parser = argparse.ArgumentParser(description='Cronohub')
parser.add_argument('-a', action="store", default="scp", type=str, dest="plugin")
args = parser.parse_args()
archiver_plugin = None


def get_repo_list() -> List[Repository.Repository]:
    """
    Gather a list of remote forks for a given user.
    Only repositories are selected for which the given user is an owner.
    This prevents the inclusion of Company based forks.

    :return: List[Repository.Repository]
        A list of remote forks for the current user.
    """
    g = Github(os.environ['CRONO_GITHUB_TOKEN'])
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


def load_from_plugin_folder() -> bool:
    filepath = Path.home() / '.config' / 'cronohub' / 'plugins'
    if not filepath.exists():
        return False
    return load_plugin(filepath)


def load_from_resource_folder() -> bool:
    filepath = pkg_resources.resource_filename('cronohub_plugins', '.')
    return load_plugin(filepath)


def load_plugin(filepath: Path) -> bool:
    global archiver_plugin
    path = Path(filepath)
    found = False
    plugin = ''
    for p in path.iterdir():
        if args.plugin in str(p):
            found = True
            plugin = p
            break

    if not found:
        return False

    archiver_plugin = import_module("cronohub_plugins." + args.plugin, plugin)
    return True


def load_plugin_with_fallback():
    """
    First: ~/.config/cronohub/plugins
        Return False if fails
    Second: site-packages/cronohub-plugins
        Returns False if fails
    If the second stage fails the program exists with status code 1.
    """
    if load_from_plugin_folder():
        logger.info("plugin loaded successfully")
    elif load_from_resource_folder():
        logger.info("plugin loaded successfully")
    else:
        print('plugin %s not found in ~/.config/cronohub/plugins or site-packages' % args.plugin)
        sys.exit(1)


def archive(f: str):
    """
    Archive uses the set plugin to archive a file located at `f`.
    """
    logger.info("archiving %s with plugin %s" % (f, args.plugin))
    archiver_plugin.archive(f)


def download_and_archive(repo_url: Repourl):
    """
    Download a single URL. This is used by `download_urls` as the function
    to map to.
    """
    url, name = repo_url
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = "{}_{}.zip".format(name, timestr)
    target = Path.cwd() / "target" / filename
    logger.info("downloading: %s, to: %s with url: %s" % (name, target, url))
    urlretrieve(url, target)
    archive(str(target))


def download_and_archive_urls(urls: List[Repourl]):
    """
    Multithreaded url downloader and archiver. As soon as a url is finished
    downloading it will be sent to the archiver function. Essentially this will
    also allow for multithreaded archiving. We could separate the two processes
    and configure the archiving with a higher thread count, but since the bottleneck
    would be the github api and downloading process it makes sense to upload as soon
    as a download is finished instead of waiting for them all to finish and then
    upload at a higher thread count.
    """
    target = Path.cwd() / "target"
    if not target.exists():
        os.makedirs(str(target))

    with Pool(5) as p:
        p.map(download_and_archive, urls)


def main():
    """
    The main of cronohub. Gathers the list of repositories to archive
    and filters them based on a `.repos_list` file that can be located
    under `~/.config/cronohub/.repo_list`. This file contains a list
    of repository names which the user wishes to archive. Anything else
    will be ignored.
    :return: None
    """
    swag = """
     _______  ______    _______  __    _  _______  __   __  __   __  _______
    |       ||    _ |  |       ||  |  | ||       ||  | |  ||  | |  ||  _    |
    |       ||   | ||  |   _   ||   |_| ||   _   ||  |_|  ||  | |  || |_|   |
    |       ||   |_||_ |  | |  ||       ||  | |  ||       ||  |_|  ||       |
    |      _||    __  ||  |_|  ||  _    ||  |_|  ||       ||       ||  _   |
    |     |_ |   |  | ||       || | |   ||       ||   _   ||       || |_|   |
    |_______||___|  |_||_______||_|  |__||_______||__| |__||_______||_______|

    Beginning archiving...
    """
    print('%s %s %s' % (fg('cyan'), swag, attr('reset')))

    if "CRONO_GITHUB_TOKEN" not in os.environ:
        print("Please set up a token by CRONO_GITHUB_TOKEN=<token>.")
        sys.exit(1)

    # Load the plugin before trying to download a 100 archives only to
    # find that the plugin was not copied where it should have been.
    load_plugin_with_fallback()

    repo_list = Path.home() / '.config' / 'cronohub' / '.repo_list'
    only = []
    if repo_list.is_file():
        logger.info('found configuration file... syncing repos from file')
        with open(str(repo_list)) as conf:
            for line in conf:
                only.append(line.strip())

    logger.info('retrieving repositories for user')
    repos = get_repo_list()
    if len(only) > 0:
        repos = list(filter(lambda r: r.name in only, repos))

    logger.info('Gathering archive urls for %d repositories.' % len(repos))
    urls = gather_archive_urls(repos)
    logger.info('Downloading archives.')
    download_and_archive_urls(urls)
    logger.info('All done. Good bye.')
