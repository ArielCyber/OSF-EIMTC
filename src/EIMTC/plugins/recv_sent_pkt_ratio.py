from nfstream import NFPlugin

class RecvSentPacketRatio(NFPlugin):
    '''
        The ratio of the number of received packets to the number of sent packets.
        = recv/sent.
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def on_expire(self, flow):
        flow.udps.sent_recv_packet_ratio =  flow.dst2src_packets / flow.src2dst_packets

