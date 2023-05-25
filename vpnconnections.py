import time
from openvpn import OpenVPN
from wireguard import WireGuard
from vpnsession import VPNSession
import libtorrent as lt
import time
import sys
import json
import os
import datetime


class VPNConnections:
    def __init__(self, config_file):
        self.vpns = []

        # Load the configuration file
        with open(config_file, 'r') as f:
            self.config = json.load(f)

    def setup_vpns(self):
        # Initialize all OpenVPN connections
        for provider, provider_config in self.config['OpenVPN'].items():
            credentials = provider_config['credentials']
            for config_file in provider_config['endpoints']:
                if not os.path.exists(config_file):
                    print(f"Config file {config_file} does not exist, skipping")
                    continue
                vpn = OpenVPN(config_file, credentials)
                vpn.setup()

                if not vpn.interface:
                    vpn.reconnect()

                if vpn.interface:
                    self.vpns.append(vpn)

                print(f"{provider} OpenVPN connection with config file {config_file} - {vpn.get_info()}")

        # Initialize all WireGuard connections
        for config_file in self.config['WireGuard']:
            if not os.path.exists(config_file):
                print(f"Config file {config_file} does not exist, skipping")
                continue
            vpn = WireGuard(config_file)
            vpn.setup()

            if not vpn.interface:
                vpn.reconnect()

            if vpn.interface:
                self.vpns.append(vpn)

            print(f"WireGuard connection with config file {config_file} - {vpn.get_info()}")

    def get_vpns(self):
        return self.vpns

    def disconnect_all(self):
        for vpn in self.vpns:
            vpn.disconnect()