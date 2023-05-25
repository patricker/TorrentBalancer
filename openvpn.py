import subprocess
import os
import re
import tempfile
from vpn import VPN


class OpenVPN(VPN):
    def __init__(self, config_file: str, credentials: dict, route_nopull=True):
        """
        Initialize the OpenVPN instance with a configuration file and credentials.
        """
        super().__init__(config_file)
        self.username = credentials['username']
        self.password = credentials['password']
        self.process = None
        self.local_ip = None
        self.interface = None
        self.credentials_file = None
        self.route_nopull = route_nopull
        self.health_check_thread = None

    def _write_credentials(self):
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as f:
            self.credentials_file = f.name
            f.write(self.username + '\n' + self.password + '\n')

    def setup(self):
        """
        Setup the OpenVPN connection.
        """
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f'OpenVPN configuration file "{self.config_file}" not found.')
        
        self._write_credentials()
        print(f"Connecting... {self.config_file}")
        args = ['openvpn', '--config', self.config_file, '--auth-user-pass', self.credentials_file]
        if self.route_nopull:
            args.append('--route-nopull')
        self.process = subprocess.Popen(args, stdout=subprocess.PIPE, universal_newlines=True)

        # Scan stdout for the local IP address and interface
        while True:
            output = self.process.stdout.readline().strip()
            if output == '' and self.process.poll() is not None:
                break
            if output:
                ip_and_interface_match = re.search(r'net_addr_v4_add: ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+).*dev (\w+)', output)
                if ip_and_interface_match:
                    self.local_ip = ip_and_interface_match.group(1)
                    self.interface = ip_and_interface_match.group(2)
                    break

    def get_interface(self):
        """
        Get the interface name used by the OpenVPN connection.
        """
        return self.interface

    def get_ip(self):
        """
        Get the IP address assigned by the OpenVPN connection.
        """
        return self.local_ip
    
    def get_info(self):
        """
        Get the information about the OpenVPN connection.
        """
        return {"local_ipv4": self.get_ip(), "interface": self.get_interface()}

    def disconnect(self):
        """
        Disconnect the OpenVPN connection.
        """
        self.process.terminate()
        os.remove(self.credentials_file)

    def reconnect(self):
        """
        Reconnect the OpenVPN connection.
        """
        print(f"Reconnecting... {self.config_file}")
        self.disconnect()
        self.setup()
