from nfstream import NFStreamer, NFPlugin
import numpy as np
from scapy.all import IP, TCP

class ProtocolHeaderFields(NFPlugin):
    '''
    wip
    '''
    def __init__(self, n_packets=32):
        self.n_packets = n_packets
    
    def on_init(self, packet, flow):
        flow.udps.protocol_header_fields_n_packets = self.n_packets
        flow.udps.protocol_header_fields = np.zeros((self.n_packets,4), dtype=np.uint32)
        
        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        if flow.bidirectional_packets <= self.n_packets and packet.protocol in [6, 17]: # TCP or UDP only.
            flow.udps.protocol_header_fields[flow.bidirectional_packets-1] = [
                packet.direction,
                packet.payload_size,
                packet.delta_time,   
                IP(packet.ip_packet)[TCP].window if packet.protocol==6 else 0
            ]

    def on_expire(self, flow):
        matrix = []
        for row in flow.udps.protocol_header_fields:
            matrix.append(list(row))
            
        flow.udps.protocol_header_fields = matrix


    @staticmethod
    def preprocess(dataframe):
        import ast
        # validate
        assert 'udps.protocol_header_fields' in dataframe.columns, "Column 'udps.protocol_header_fields' not found."
        assert isinstance(dataframe['udps.protocol_header_fields'].iloc[0], str), "Values in column 'udps.protocol_header_fields' are already processed."
        
        dataframe['udps.protocol_header_fields'] = dataframe['udps.protocol_header_fields'].apply(ast.literal_eval)
        
        