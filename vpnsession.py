from vpn import VPN

class VPNSession:
    def __init__(self, vpn:VPN, ses, pieces):
        self.vpn = vpn
        self.ses = ses
        self.h = ses.get_torrents()[0]
        self.verified_pieces = []
        self.non_verified_pieces = pieces.copy()
        for piece in pieces:
            self.h.piece_priority(piece, 1)

    def verify_pieces(self):
        # Verify pieces downloaded
        for piece in self.non_verified_pieces.copy():
            if self.h.have_piece(piece):
                self.verified_pieces.append(piece)
                self.non_verified_pieces.remove(piece)

    def needs_more_pieces(self):
        # Verify downloaded pieces and check if it needs more pieces
        self.verify_pieces()
        return len(self.non_verified_pieces) <= 2

    def assign_piece(self, piece):
        self.h.piece_priority(piece, 1)
        self.non_verified_pieces.append(piece)