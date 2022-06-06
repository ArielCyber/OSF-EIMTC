from nfstream import NFPlugin


class SmallPacketPayloadRatio(NFPlugin):
    '''
        The ratio of number of small packets for direction X to the the total number of packets
        in direction X,
        for each direction x in {src2dst, dst2src}.
    '''
    def __init__(self, small_size = 32, **kwargs):
        '''
            small_size: the size (in bytes) of the payload that
            a packet is considered to be small (i.e, payload size < small_size).
        '''
        super().__init__(**kwargs)
        self.small_size = small_size

    def on_init(self, packet, flow):
        '''
        on_init(self, packet, flow): Method called at flow creation.
        '''
        flow.udps.src2dst_small_packet_payload_packets = 0
        flow.udps.src2dst_small_packet_payload_ratio   = 0
        flow.udps.dst2src_small_packet_payload_packets = 0
        flow.udps.dst2src_small_packet_payload_ratio   = 0
        

        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        if packet.payload_size < self.small_size:
            if packet.direction == 0: # src2dst
                flow.udps.src2dst_small_packet_payload_packets += 1
            else:
                flow.udps.dst2src_small_packet_payload_packets += 1

    def on_expire(self, flow):
        if flow.src2dst_packets != 0:
            flow.udps.src2dst_small_packet_payload_ratio = (flow.udps.src2dst_small_packet_payload_packets 
                                                            / flow.src2dst_packets)
        if flow.dst2src_packets != 0:
            flow.udps.dst2src_small_packet_payload_ratio = (flow.udps.dst2src_small_packet_payload_packets
                                                            / flow.dst2src_packets)
