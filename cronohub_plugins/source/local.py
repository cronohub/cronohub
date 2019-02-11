import os
from cronohub import source_plugin
from pathlib import Path

class SourcePlugin(source_plugin.CronohubSourcePlugin):
    def __init__(self):
        print('initialising local source plugin')

    def validate(self):
        print('validating')
        if 'CRONOHUB_LOCAL_SOURCE' not in os.environ:
            print('Please set CRONOHUB_LOCAL_SOURCE to a directory from which to uploda files from.')
            return False
        return True

    def help(self):
        print('Define a local folder from which to upload all files from to target.')

    def fetch(self):
        folder = os.environ['CRONOHUB_LOCAL_SOURCE']
        result = []
        l = list(Path(folder).rglob("*.*"))
        for p in l:
            result.append((os.path.basename(p), str(p)))
        return result