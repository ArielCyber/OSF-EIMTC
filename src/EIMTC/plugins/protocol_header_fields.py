from nfstream import NFStreamer, NFPlugin
import numpy as np
from scapy.all import IP, TCP

class ProtocolHeaderFields(NFPlugin):
    ''' ProtocolHeaderFields |
    Extracts 4 features for `n_packets` packets. Packet direction, payload size, delta time
    and TCP window size if TCP, value is set to zero if UDP. 
    
    Feature Outputs:
        - udps.protocol_header_fields: output shape of (`n_packets`, 4). Hence `n_packets` rows and 4 columns per row where each column contains the respective feature extracted from the packet. [dir, size, time, win]
    
    Paper:
        "Network Traffic Classifier With Convolutional and Recurrent Neural Networks for Internet of Things"
        
        By:
            - Manuel Lopez-Martin (Senior Member, IEEE).
            - Belen Carro.
            - Antonio Sanchez-Esguevillas (Senior Member, IEEE).
            - Jaime Lloret (Senior Member, IEEE).
    '''
    def __init__(self, n_packets=32):
        '''
        Args:
            `n_packets` (int): The number of packets to process.
        '''
        self.n_packets = n_packets
    
    def on_init(self, packet, flow):
        ''' '''
        flow.udps.protocol_header_fields_n_packets = self.n_packets
        flow.udps.protocol_header_fields = np.zeros((self.n_packets,4), dtype=np.uint32)
        
        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        ''' '''
        if flow.bidirectional_packets <= self.n_packets and packet.protocol in [6, 17]: # TCP or UDP only.
            flow.udps.protocol_header_fields[flow.bidirectional_packets-1] = [
                packet.direction,
                packet.payload_size,
                packet.delta_time,   
                IP(packet.ip_packet)[TCP].window if packet.protocol==6 else 0
            ]

    def on_expire(self, flow):
        ''' '''
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
        
        