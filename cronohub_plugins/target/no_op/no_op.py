from cronohub import target_plugin


class TargetPlugin(target_plugin.CronohubTargetPlugin):
    def __init__(self):
        print('initialising no op target plugin')

    def validate(self):
        print('validating')
        return True

    def help(self):
        print('No-Op means no operation.')

    def archive(self, files):
        print('archiving: ', files)
