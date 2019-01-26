import os
import time
from cronohub import source_plugin
from multiprocessing import Pool
from pathlib import Path
from typing import List
from urllib.request import urlretrieve
from github import Github, Repository


class SourcePlugin(source_plugin.CronohubSourcePlugin):
    """
    GithubPlugin: This is a CronoHub source plugin. The source
    is Github repositories for a given user. The user is determined
    through the provided token. No other authentication is required.
    Methods:
        __init__: will initialise this plugin
        validate: validates if the plugin's required settings are met.
        help: displays a helpful message of what the plugin requires.
        fetch: the brain of the plugin will fetch the user's repositories.
    """
    def __init__(self):
        print('initializing github source plugin')

    def validate(self) -> bool:
        print('validating requirements')
        if "CRONO_GITHUB_TOKEN" not in os.environ:
            print("Please set up a token by CRONO_GITHUB_TOKEN=<token>.")
            return False
        return True

    def help(self):
        print('''
        Help (github source plugin):
            - Environment Property:
                CRONO_GITHUB_TOKEN: a token with access to listing repositories for a given user.
        ''')

    def download(self, repo_url: (str, str)) -> (str, str):
        """
        Download a single URL. This is used by `download_urls` as the function
        to map to.
        """
        url, name = repo_url
        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = "{}_{}.zip".format(name, timestr)
        target = Path.cwd() / "target" / filename
        urlretrieve(url, target)
        return target, name

    def download_urls(self, urls):
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
        result = []
        with Pool(5) as p:
            result.append(p.map(self.download, urls))
        return result[0]

    def get_repo_list(self) -> List[Repository.Repository]:
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

    def gather_archive_urls(self, repos: List[Repository.Repository]):
        """
        Gather a list of URLs for the repositories.
        """
        return list(map(lambda r: (r.get_archive_link(archive_format="zipball"), r.name), repos))

    def fetch(self):
        repo_list = Path.home() / '.config' / 'cronohub' / '.repo_list'
        only = []
        if repo_list.is_file():
            with open(str(repo_list)) as conf:
                for line in conf:
                    only.append(line.strip())

        repos = self.get_repo_list()
        if len(only) > 0:
            repos = list(filter(lambda r: r.name in only, repos))

        urls = self.gather_archive_urls(repos)
        return self.download_urls(urls)
