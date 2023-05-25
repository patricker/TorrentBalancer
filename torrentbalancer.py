import time
from vpnconnections import VPNConnections
from vpnsession import VPNSession
import libtorrent as lt
import time
import sys
import json
import os
import datetime

class TorrentBalancer:
    def __init__(self, torrent_path:str, vpn_config_path:str):
        self.torrent_path = torrent_path
        self.vpn_config_path = vpn_config_path
        self.vpn_connections = VPNConnections(vpn_config_path)
        self.torrent_info = lt.torrent_info(torrent_path)
        self.num_pieces = self.torrent_info.num_pieces()
        self.torrent_size = self.torrent_info.total_size()
        self.free_pieces = list(range(self.num_pieces))
        self.initial_pieces = 5
        self.piece_assignment = 3
        self.vpn_sessions = []

    def print_status(self, total_pieces):
        total_download_rate = 0
        total_upload_rate = 0
        total_num_peers = 0
        total_progress = 0
        total_validated_pieces = 0
        total_states = []

        for session in self.vpn_sessions:
            s = session.h.status()

            total_validated_pieces += len(session.verified_pieces)
            total_download_rate += s.download_rate
            total_upload_rate += s.upload_rate
            total_num_peers += s.num_peers
            total_progress += s.progress
            total_states.append(str(s.state).split('.')[-1])  # Extract just the state name

        avg_progress = (total_progress / len(self.vpn_sessions)) * 100

        print(f'\r{avg_progress:.2f}% complete (down: {total_download_rate / 1000:.1f} kB/s up: {total_upload_rate / 1000:.1f} kB/s peers: {total_num_peers}) '
              f'States: {", ".join(total_states)} Free pieces: {len(self.free_pieces)} Piece Ratio: {total_validated_pieces}/{total_pieces}', end=' ')

        sys.stdout.flush()

    def start(self):
        self.vpn_connections.setup_vpns()
        arr = self.vpn_connections.get_vpns()

        start_time = datetime.datetime.now()

        for i in range(len(arr)):
            vpn = arr[i]

            ses = lt.session({'outgoing_interfaces': vpn.get_info()['interface'],'listen_interfaces': vpn.get_info()['local_ipv4'] + ':6881'})
            ses.pause()

            h = ses.add_torrent({'ti': self.torrent_info, 'save_path': '.'})

            assigned_pieces = [self.free_pieces.pop(0) for _ in range(self.piece_assignment) if self.free_pieces]
            self.vpn_sessions.append(VPNSession(vpn, ses, assigned_pieces))

            ses.resume()

        while self.free_pieces or not all(vpn_ses.h.is_finished() for vpn_ses in self.vpn_sessions):
            self.print_status(self.num_pieces)

            for vpn_ses in self.vpn_sessions:
                while vpn_ses.needs_more_pieces() and self.free_pieces:
                    for _ in range(self.piece_assignment):
                        if self.free_pieces:
                            vpn_ses.assign_piece(self.free_pieces.pop(0))
                        else:
                            break

            time.sleep(0.1)

        end_time = datetime.datetime.now()

        self.vpn_connections.disconnect_all()

        duration = end_time - start_time

        print("Start time: ", start_time)
        print("End time: ", end_time)
        print("Total duration: ", duration.total_seconds(), "seconds")

        average_download_speed = self.torrent_size / duration.total_seconds()
        print("Average download speed: ", average_download_speed / 1000, "kB/s")

        print("All torrents complete")