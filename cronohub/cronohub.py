import argparse
import sys
from importlib import import_module
from pathlib import Path

import pkg_resources
from colored import attr, fg

parser = argparse.ArgumentParser(description='Cronohub')
parser.add_argument('-s', action="store", default="github", type=str, dest="source")
parser.add_argument('-t', action="store", default="scp", type=str, dest="target")
args = parser.parse_args()


def load_from_plugin_folder(t: str, name: str):
    filepath = Path.home() / '.config' / 'cronohub' / 'plugins'
    if not filepath.exists():
        return None
    return load_plugin(t, name, filepath)


def load_from_resource_folder(t: str, name: str):
    filepath = pkg_resources.resource_filename('cronohub_plugins', '.')
    return load_plugin(t, name, filepath)


def load_plugin(t: str, name: str, filepath: Path):
    path = Path(filepath) / t
    found = False
    plugin = ''
    for p in path.iterdir():
        if name in str(p):
            found = True
            plugin = p
            break

    if not found:
        return None

    return import_module("cronohub_plugins." + t + "." + name, plugin)


def load_plugin_with_fallback(t: str, name: str):
    """
    First: ~/.config/cronohub/plugins
        Return False if fails
    Second: site-packages/cronohub-plugins
        Returns False if fails
    If the second stage fails the program exists with status code 1.
    """
    p = load_from_plugin_folder(t, name)
    if p:
        return p
    else:
        return load_from_resource_folder(t, name)


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

    # Load the plugin before trying to download a 100 archives only to
    # find that the plugin was not copied where it should have been.
    source_plugin = load_plugin_with_fallback('source', args.source)
    if not source_plugin:
        print("source plugin '%s' not found!" % args.source)
        sys.exit(1)
    target_plugin = load_plugin_with_fallback('target', args.target)
    if not target_plugin:
        print("target plugin '%s' not found!" % args.target)
        sys.exit(1)

    sp = source_plugin.SourcePlugin()
    sp.validate()
    # Display help if help is called.

    tp = target_plugin.TargetPlugin()
    tp.validate()
    # display help if requested

    results = sp.fetch()
    tp.archive(results)

    print('All done. Good bye.')
    # Load the source and target.
    # Call the source which should provide a list of files to the archiver
    # call archiver.
    # Implement concurrent archiving too... Since now they are decopuled.

