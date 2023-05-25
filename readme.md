# TorrentBalancer

TorrentBalancer is a Python library which allows users to download torrent files using multiple VPN connections simultaneously. It uses the libtorrent library with Python bindings for handling torrent downloads. This library leverages multiple VPN connections (OpenVPN and/or WireGuard) to download different pieces of the same torrent file, potentially enhancing download/upload speed.

- [TorrentBalancer](#torrentbalancer)
  - [Technical Details: Multiple VPN Torrent Downloading](#technical-details-multiple-vpn-torrent-downloading)
  - [Installation](#installation)
  - [Permissions](#permissions)
  - [Configuration](#configuration)
    - [Example](#example)
    - [OpenVPN Notes](#openvpn-notes)
    - [Wireguard Notes](#wireguard-notes)
  - [Usage](#usage)
  - [Innacurate Speed Readings](#innacurate-speed-readings)
  - [Legal Disclaimer](#legal-disclaimer)
  - [License](#license)


## Technical Details: Multiple VPN Torrent Downloading

TorrentBalancer uses multiple VPN connections to download a torrent file. Here's how it works:

1. **Setup VPN Connections**: TorrentBalancer starts by reading a configuration file which contains the VPN details. Both OpenVPN and WireGuard connections are supported. Each VPN connection is individually established.

2. **Session Creation**: For each VPN connection, a separate libtorrent session is created in a paused state. This effectively means that each VPN is a separate torrent client running independently from each other. Each session is bound to the specific interface that the VPN connection provides. This ensures that the traffic of that session is routed through the appropriate VPN.

3. **Torrent Addition**: The torrent file is added to each session, but before resuming the session, some pieces of the torrent are assigned to each session. All pieces not assigned to a session are set to a priority of 0, and assigned pieces are assigned a priority of 1; so each session starts downloading different parts of the file.

4. **Piece Assignment**: Each session starts with a few pieces assigned. The list of pieces is controlled centrally, and each time a session is getting low on pieces to download, they are assigned from the central list automatically. This ensures that each session downloads a unique part of the file, maximizing the overall download speed.

5. **Session Resumption**: Once the initial setup is done, the sessions are resumed and they all start downloading their assigned pieces.

6. **Active Monitoring and Management**: TorrentBalancer actively monitors the progress of each session. When a session is running low on assigned pieces to download, more pieces are assigned to it from the central list. This process continues until all pieces are downloaded.

7. **Completion**: Once all pieces are downloaded and all sessions are finished, the VPN connections are closed. The individual pieces downloaded by different sessions form the complete torrent file.

Each session works independently, and as long as there are more pieces to download, they can continue to do so without waiting for other sessions. This allows TorrentBalancer to fully utilize all the VPN connections to maximize the download speed.

## Installation
You will need the Python wrapper for libtorrent to be installed on your system to use TorrentBalancer.

```bash
pip3 install -r requirements.txt
```

## Permissions
Creating VPN connections and tearing them down during script execution generally require root/admin permissions. Trying to run the script without the necessary permissions will just cause the VPN connections to fail.

## Configuration
You need to set up VPN connections for TorrentBalancer to use. The configuration is done in a JSON file, with the following structure:

```json
{
    "OpenVPN": {
        "ProviderName": {
            "credentials": {
                "username": "your_username",
                "password": "your_password"
            },
            "endpoints": [
                "/path/to/openvpn_config1.ovpn",
                "/path/to/openvpn_config2.ovpn"
            ]
        }
    },
    "WireGuard": [
        "/path/to/wireguard_config1.conf",
        "/path/to/wireguard_config2.conf"
    ]
}
```

Replace "ProviderName" with the name of your VPN provider. Replace "your_username" and "your_password" with your VPN credentials. You can add paths to as many OpenVPN or WireGuard configuration files as you want.

### Example
```json
{
    "OpenVPN": {
        "PIA": {
            "credentials": {
                "username": "pia_username",
                "password": "pia_password"
            },
            "endpoints": [
                "/home/us_california.ovpn",
                "/home/us_denver.ovpn",
                "/home/us_seattle.ovpn",
                "/home/us_west.ovpn",
                "/home/ca_ontario.ovpn"
            ]
        },
        "NordVPN": {
            "credentials": {
                "username": "nordusername",
                "password": "nordpassword"
            },
            "endpoints": [
                "/home/us10011.nordvpn.com.udp1194.ovpn",
                "/home/us9539.nordvpn.com.udp1194.ovpn"
            ]
        }
    },
    "WireGuard": [
    ]
}

```

### OpenVPN Notes
While Private Internet Access (PIA) supports "unlimited" connections, they need them to be to different locations. Adding the same location multiple times causes strange behavior due to how PIA assigns IP addresses.

NordVPN does not want to allow me to setup more than one or two connections at a time.

### Wireguard Notes
When using WireGuard configuration files, make sure to include the line `Table = off` in each of the configuration files. This prevents WireGuard from changing your system's routing table.

## Usage
Please ensure that the OpenVPN and WireGuard configuration files work correctly on their own before using them in TorrentBalancer. This can be done by manually setting up a VPN connection with each of the configuration files.

To use TorrentBalancer, you can run the provided `main.py` script. The script requires two arguments: the path to a local torrent file, and the path to a VPN configuration file.

You can run the script from the command line like this:

```bash
python main.py /path/to/your/torrent_file.torrent /path/to/your/vpn_config.json
```

Replace /path/to/your/torrent_file.torrent with the path to the torrent file you want to download, and replace /path/to/your/vpn_config.json with the path to your VPN configuration file.

## Innacurate Speed Readings
Libtorrent does not accurately report download speeds in real time when used in this way. The actual average speed is reported when the torrent finishes downloading.

## Legal Disclaimer
Please follow all local and international laws regarding the use of VPNs and torrenting. This code is intended for educational purposes only.

## License
TorrentBalancer is released under the MIT license. Please refer to the LICENSE file for details.
