from nfstream import NFStreamer, NFPlugin
import numpy as np
from scapy.all import IP, TCP

class ProtocolHeaderFields_Extended(NFPlugin):
    ''' ProtocolHeaderFields_Extended |
    Extracts 6 features for `n_packets` packets. Packet direction, payload size, delta time
    , TCP window size if TCP, value is set to zero if UDP, TCP number of options if TCP, value is set to zero if UDP
    and Time-To-Live (TTL) of packet.
    
    Feature Outputs:
        - udps.protocol_header_fields_enh: output shape of (`n_packets`, 6). Hence `n_packets` rows and 6 columns per row where each column contains the respective feature extracted from the packet. [dir, size, time, win, opt, ttl]
    
    Inspired by:
        "Network Traffic Classifier With Convolutional and Recurrent Neural Networks for Internet of Things"
    '''
    def __init__(self, n_packets=32):
        '''
        Args:
            `n_packets` (int): The number of packets to process.
        '''
        self.n_packets = n_packets
    
    def on_init(self, packet, flow):
        ''' '''
        flow.udps.protocol_header_fields_n_packets_enh = self.n_packets
        flow.udps.protocol_header_fields_enh = np.zeros((self.n_packets, 6), dtype=np.uint32)
        
        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        ''' '''
        if flow.bidirectional_packets <= self.n_packets and packet.protocol in [6,17]: # TCP or UDP only.
            scapy_ip = IP(packet.ip_packet)
            scapy_tcp = scapy_ip[TCP] if packet.protocol==6 else None
            flow.udps.protocol_header_fields_enh[flow.bidirectional_packets-1] = [
                packet.direction,
                packet.payload_size,
                packet.delta_time,   
                scapy_tcp.window if scapy_tcp else 0,
                len(scapy_tcp.options) if scapy_tcp else 0, # Length/number of TCP options.
                scapy_ip.ttl, # IP ttl
            ]
            

    def on_expire(self, flow):
        ''' '''
        matrix = []
        for row in flow.udps.protocol_header_fields_enh:
            matrix.append(list(row))
            
        flow.udps.protocol_header_fields_enh = matrix


    @staticmethod
    def preprocess(dataframe):
        import ast
        # validate
        assert 'udps.protocol_header_fields_enh' in dataframe.columns, "Column 'udps.protocol_header_fields_enh' not found."
        assert isinstance(dataframe['udps.protocol_header_fields_enh'].iloc[0], str), "Values in column 'udps.protocol_header_fields_enh' are already processed."
        
        dataframe['udps.protocol_header_fields_enh'] = dataframe['udps.protocol_header_fields_enh'].apply(ast.literal_eval)
        
        