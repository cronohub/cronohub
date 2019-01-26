import os
from paramiko import SSHClient, SSHConfig
from scp import SCPClient
from cronohub import target_plugin


class TargetPlugin(target_plugin.CronohubTargetPlugin):
    def __init__(self):
        print('initialising SCP target plugin')

    def validate(self):
        print('validating')
        if "CRONOHUB_SCP_HOST" not in os.environ:
            print('please provide CRONOHUB_SCP_HOST environment property for archiving.')
            return False
        return True

    def help(self):
        print('''
        Help (scp target plugin):
            - Environment Property:
                CRONOHUB_SCP_HOST: host name to connect to. This can be one of two:
            #1: a hostname as defined under ~/.ssh/config file exp:
                Host pi
                    HostName 1.2.3.4
                    User username
                    Port 1234
                    IdentityFile ~/.ssh/id_rsa

                In this case the environment property would be `pi`.
            #2: an IP address or a web site address in which case it will be tried as is.
        ''')

    def archive(self, files):
        print("scp-ing: ", files)
        ssh = SSHClient()
        ssh.load_system_host_keys()
        # locate hostname in config file if not found, try connecting directly.
        hostname = os.environ['CRONOHUB_SCP_HOST']
        # TODO: This won't work on windows...
        ssh_config_file = os.path.expanduser("~/.ssh/config")
        if os.path.exists(ssh_config_file):
            config = SSHConfig()
            with open(ssh_config_file) as f:
                config.parse(f)
        settings = config.lookup(hostname)
        if settings['hostname'] != hostname:
            ssh.connect(settings['hostname'],
                        username=settings['user'],
                        key_filename=settings['identityfile'][0],
                        port=settings['port'])
        else:
            ssh.connect(hostname)

        scp = SCPClient(ssh.get_transport())
        for file in files:
            scp.put(file[0])
