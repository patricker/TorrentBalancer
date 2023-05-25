import subprocess
import os
import re

from vpn import VPN

class WireGuard(VPN):
    """
    WireGuard VPN class.
    NOTE: Table = off must be set in the WireGuard configuration file.
    """
    def __init__(self, config_file: str):
        """
        Initialize the WireGuard instance with a configuration file.
        """
        super().__init__(config_file)
        self.process = None
        self.interface = None

    def setup(self):
        """
        Setup the WireGuard connection.
        """
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f'WireGuard configuration file "{self.config_file}" not found.')
        
        # It's not uncommon for a connection to already exist. Run disconnect first.
        self.disconnect()
        
        print(f"Connecting... {self.config_file}")
        args = ['wg-quick', 'up', self.config_file]
        self.process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        # Extract the interface from the config file name
        self.interface = os.path.splitext(os.path.basename(self.config_file))[0]
        stdout, stderr = self.process.communicate()

        ip_and_interface_match = re.search(r'ip -4 address add ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+).*dev (\w+)', stdout + stderr)
        if ip_and_interface_match:
            self.local_ip = ip_and_interface_match.group(1)
            self.interface = ip_and_interface_match.group(2)
        else:
            print("IP and Interface not found in the output.")

    def get_interface(self):
        """
        Get the interface name used by the WireGuard connection.
        """
        return self.interface

    def get_ip(self):
        """
        Get the IP address assigned by the WireGuard connection.
        """
        return self.local_ip
    
    def get_info(self):
        """
        Get the information about the WireGuard connection.
        """
        return {"local_ipv4": self.get_ip(), "interface": self.get_interface()}
        
    def disconnect(self):
        """
        Disconnect the WireGuard connection.
        """
        print(f"Disconnecting... {self.config_file}")
        args = ['wg-quick', 'down', self.config_file]
        subprocess.run(args)

    def reconnect(self):
        """
        Reconnect the WireGuard connection.
        """
        print(f"Reconnecting... {self.config_file}")
        self.disconnect()
        self.setup()