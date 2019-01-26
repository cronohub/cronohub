import argparse
import sys
from importlib import import_module
from pathlib import Path

import pkg_resources
from colored import attr, fg

parser = argparse.ArgumentParser(description='Cronohub')
parser.add_argument('-s',
                    action="store",
                    default="github",
                    type=str,
                    dest="source",
                    help="Name of the source plugin.")
parser.add_argument('-t',
                    action="store",
                    default="scp",
                    type=str,
                    dest="target",
                    help="Name of the target plugin.")
parser.add_argument('--source-help',
                    action="store",
                    default=None,
                    type=str,
                    dest="source_help",
                    help="Display help for a given source plugin.")
parser.add_argument('--target-help',
                    action="store",
                    default=None,
                    type=str,
                    dest="target_help",
                    help="Display help for a given target plugin.")
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


def display_help(t: str):
    if t == 'source':
        plugin = load_plugin_with_fallback(t, args.source_help)
        if not plugin:
            print('plugin %s not found' % args.source_help)
            sys.exit(1)
        plugin.SourcePlugin().help()
    else:
        plugin = load_plugin_with_fallback(t, args.target_help)
        if not plugin:
            print('plugin %s not found' % args.target_help)
            sys.exit(1)
        plugin.TargetPlugin().help()
    sys.exit(0)


def main():
    """
    The main of cronohub. Initialize the two plugins, source and target.
    If either of them is missing, output an error message. If all is well,
    call the plugin's validate function to see if everything is set up for
    the plugin that it needs. If all is well again, call fetch and archive.
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

    if args.source_help:
        display_help('source')

    if args.target_help:
        display_help('target')

    source_plugin = load_plugin_with_fallback('source', args.source)
    if not source_plugin:
        print("source plugin %s'%s'%s not found!" % (fg('red'), args.source, attr('reset')))
        sys.exit(1)
    target_plugin = load_plugin_with_fallback('target', args.target)
    if not target_plugin:
        print("target plugin %s'%s'%s not found!" % (fg('red'), args.target, attr('reset')))
        sys.exit(1)

    sp = source_plugin.SourcePlugin()
    if not sp.validate():
        sys.exit(1)

    tp = target_plugin.TargetPlugin()
    if not tp.validate():
        sys.exit(1)

    results = sp.fetch()
    tp.archive(results)

    print('All done. Good bye.')
