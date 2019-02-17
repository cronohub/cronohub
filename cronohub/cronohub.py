import argparse
import sys
from importlib.util import spec_from_file_location, module_from_spec
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
    n = ""
    if t == "source":
        n = name + ".SourcePlugin"
    else:
        n = name + ".TargetPlugin"
    p = plugin / name
    p = str(p) + ".py"
    spec = spec_from_file_location(n, p)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def display_help(t: str):
    if t == 'source':
        plugin = load_from_plugin_folder(t, args.source_help)
        if not plugin:
            print('plugin %s not found' % args.source_help)
            sys.exit(1)
        plugin.SourcePlugin().help()
    else:
        plugin = load_from_plugin_folder(t, args.target_help)
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

    source_plugin = load_from_plugin_folder('source', args.source)
    if not source_plugin:
        print("source plugin %s'%s'%s not found!" % (fg('red'), args.source, attr('reset')))
        sys.exit(1)
    target_plugin = load_from_plugin_folder('target', args.target)
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
