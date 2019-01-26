import argparse
import sys
from importlib import import_module
from pathlib import Path

import pkg_resources
from colored import attr, bg, fg

parser = argparse.ArgumentParser(description='Cronohub')
parser.add_argument('-s', action="store", default="github", type=str, dest="source")
parser.add_argument('-t', action="store", default="scp", type=str, dest="target")
args = parser.parse_args()
source_plugin = None
target_plugin = None


def load_from_plugin_folder() -> bool:
    filepath = Path.home() / '.config' / 'cronohub' / 'plugins'
    if not filepath.exists():
        return False
    return load_plugin(filepath)


def load_from_resource_folder() -> bool:
    filepath = pkg_resources.resource_filename('cronohub_plugins', '.')
    return load_plugin(filepath)


def load_plugin(name: str, filepath: Path) -> bool:
    global source_plugin, target_plugin
    path = Path(filepath)
    found = False
    plugin = ''
    for p in path.iterdir():
        if name in str(p):
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
        print('plugin successfully loaded')
    elif load_from_resource_folder():
        print("plugin loaded successfully")
    else:
        print('plugin %s not found in ~/.config/cronohub/plugins or site-packages' % args.plugin)
        sys.exit(1)


def archive(f: str):
    """
    Archive uses the set plugin to archive a file located at `f`.
    """
    print("archiving %s with plugin %s" % (f, args.plugin))
    archiver_plugin.archive(f)



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
    load_plugin_with_fallback()

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

