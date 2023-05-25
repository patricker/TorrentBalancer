import sys
from torrentbalancer import TorrentBalancer

def main(torrent_file, vpn_config):
    balancer = TorrentBalancer(torrent_file, vpn_config)
    balancer.start()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <torrent file path> <vpn config path>")
        sys.exit(1)

    torrent_file = sys.argv[1]
    vpn_config = sys.argv[2]
    
    main(torrent_file, vpn_config)
