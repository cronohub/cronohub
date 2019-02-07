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
        print("Gitlab config file under ~/.config/cronohub/gitlab.cfg")

    def validate(self):
        self.cfg_file = Path.home() / '.config' / 'cronohub' / 'gitlab.cfg'
        if not self.cfg_file.exists():
            print('missing configuration file from ~/.config/cronohub/gitlab.cfg')
            return False
        return True

    def get_repo_list(self):
        projects = self.gl.projects.list(owned=True)
        return projects

    def fetch(self):
        # https://gitlab.com/Skarlso/testproject/-/archive/master/testproject-master.tar
        # zipfn = "___artifacts.zip"
        # with open(zipfn, "wb") as f:
        #     build_or_job.artifacts(streamed=True, action=f.write)
        # print("downloading archives")
        self.gl = Gitlab.from_config(gitlab_id='global', config_files=[self.cfg_file])
        projects = self.get_repo_list()
        p: v4.objects.Project
        for p in projects:
            # Create the export
            # p = gl.projects.get(project)
            export = p.exports.create({})

            # Wait for the 'finished' status
            export.refresh()
            while export.export_status != 'finished':
                time.sleep(1)
                export.refresh()

            # Download the result
            with open('/tmp/export.tgz', 'wb') as f:
                export.download(streamed=True, action=f.write)