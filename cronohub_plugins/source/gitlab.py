import time
import os
from cronohub import source_plugin
from gitlab import Gitlab, v4
from pathlib import Path
from typing import List

class SourcePlugin(source_plugin.CronohubSourcePlugin):
    gl = None
    cfg_file = None

    def __init__(self):
        print("initialising gitlab archiver plugin")

    def help(self):
        print('''Help:
            Gitlab config file under ~/.config/cronohub/gitlab.cfg
            [Optional]: Environment Property: CRONOHUB_GITLAB_ID
        ''')

    def validate(self):
        self.cfg_file = Path.home() / '.config' / 'cronohub' / 'source_gitlab.ini'
        if not self.cfg_file.exists():
            print('missing configuration file from ~/.config/cronohub/source_gitlab.ini')
            return False
        return True

    def get_repo_list(self):
        projects = self.gl.projects.list(owned=True)
        return projects

    def fetch(self):
        paths = []
        gitlab_id = 'gitlab'
        if 'CRONOHUB_GITLAB_ID' in os.environ:
            gitlab_id = os.environ['CRONOHUB_GITLAB_ID']

        target = Path.cwd() / 'target'
        if not target.exists():
            os.makedirs(str(target))

        self.gl = Gitlab.from_config(gitlab_id=gitlab_id, config_files=[self.cfg_file])
        projects = self.get_repo_list()
        p: v4.objects.Project
        for p in projects:
            # Create the export
            export = p.exports.create({})

            # Wait for the 'finished' status
            export.refresh()
            while export.export_status != 'finished':
                time.sleep(1)
                export.refresh()

            timestr = time.strftime("%Y%m%d-%H%M%S")
            filename = "{}_{}.gz".format(p.name, timestr)
            t = Path.cwd() / 'target' / filename
            # (Location, Filename) tuple
            paths.append((str(t), filename))
            with open(str(t), 'wb') as f:
                export.download(streamed=True, action=f.write)
        return paths