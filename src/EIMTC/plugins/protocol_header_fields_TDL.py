from nfstream import NFStreamer, NFPlugin
import numpy as np
from scapy.all import IP, TCP

class ProtocolHeaderFieldsTDL(NFPlugin):
    ''' ProtocolHeaderFieldsTDL |
    Extracts 3 features for `n_packets` packets. Packet direction, payload size and delta time.
    This plugin use only Timestamp , Direction and Length (TDL). 
    
    Feature Outputs:
        - udps.protocol_header_fields_TDL: output shape of (`n_packets`, 3). Hence `n_packets` rows and 3 columns per row where each column contains the respective feature extracted from the packet. [dir, size, time, win]
    
    '''
    def __init__(self, n_packets=32):
        '''
        Args:
            `n_packets` (int): The number of packets to process.
        '''
        self.n_packets = n_packets
    
    def on_init(self, packet, flow):
        ''' '''
        flow.udps.protocol_header_fields_n_packets_TDL = self.n_packets
        flow.udps.protocol_header_fields_TDL = np.zeros((self.n_packets,3), dtype=np.uint32)
        
        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        ''' '''
        if flow.bidirectional_packets <= self.n_packets and packet.protocol in [6, 17]: # TCP or UDP only.
            flow.udps.protocol_header_fields[flow.bidirectional_packets-1] = [
                packet.direction,
                packet.payload_size,
                packet.delta_time,   
            ]

    def on_expire(self, flow):
        ''' '''
        matrix = []
        for row in flow.udps.protocol_header_fields_TDL:
            matrix.append(list(row))
            
        flow.udps.protocol_header_fields_TDL = matrix
        del flow.udps.protocol_header_fields_n_packets_TDL


    @staticmethod
    def preprocess(dataframe):
        import ast
        # validate
        assert 'udps.protocol_header_fields_TDL' in dataframe.columns, "Column 'udps.protocol_header_fields_TDL' not found."
        assert isinstance(dataframe['udps.protocol_header_fields_TDL'].iloc[0], str), "Values in column 'udps.protocol_header_fields_TDL' are already processed."
        
        dataframe['udps.protocol_header_fields_TDL'] = dataframe['udps.protocol_header_fields_TDL'].apply(ast.literal_eval)
        
        