import owncloud
import os
from cronohub import target_plugin


class TargetPlugin(target_plugin.CronohubTargetPlugin):
    def __init__(self):
        print('initialising no op target plugin')

    def validate(self):
        for v in [
            'CRONOHUB_OWNCLOUD_URL',
            'CRONOHUB_OWNCLOUD_USERNAME',
            'CRONOHUB_OWNCLOUD_PASSWORD'
        ]:
            if v not in os.environ:
                print("Please set %s environment variable." % v)
                return False
        return True

    def help(self):
        print('''
        OwnCloud location URL: CRONOHUB_OWNCLOUD_URL (https://username.ocloud.de)
        OwnCloud Username: CRONOHUB_OWNCLOUD_USERNAME (admin)
        OwnCloud Password: CRONOHUB_OWNCLOUD_PASSWORD (admin)
        ''')

    def archive(self, files):
        url = os.environ['CRONOHUB_OWNCLOUD_URL']
        user = os.environ['CRONOHUB_OWNCLOUD_USERNAME']
        password = os.environ['CRONOHUB_OWNCLOUD_PASSWORD']
        oc = owncloud.Client(url)
        oc.login(user, password)
        for f in files:
            print("uploading %s..." % f[0])
            oc.put_file(f[0], f[1])
