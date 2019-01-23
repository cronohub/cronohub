import os
from paramiko import SSHClient, SSHConfig
from scp import SCPClient

def archive(file: str):
    print("scp-ing: ", file)
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
    scp.put(file)