from nfstream import NFPlugin
import numpy as np
from scapy.all import IP, IPv6, raw
from pypacker.layer3 import ip
from pypacker.layer3 import ip6
import pandas as pd
import ast



class NBytes(NFPlugin):
    ''' NBytes |
    Extracts the first n_bytes from the flow, the bytes are taken
    from the transport layer payload (L4). if the flow has less than n_bytes bytes,
    then the rest of the bytes are zero-valued (padding).
        
    Paper:
        "End-to-end Encrypted Traffic Classification with One-dimensional Convolution Neural Networks".

        By:
            - Wei Wang.
            - Ming Zhu.
            - Jinlin Wang.
            - Xuewen Zeng.
            - Zhongzhen Yang.
    '''
    def __init__(self, n=784):
        '''
        Args:
            `n` (int): The number of bytes to extract from the flow's payload.
        '''
        self.n = n
    
    def on_init(self, packet, flow):
        ''' '''
        flow.udps.n_bytes_value = self.n
        flow.udps.n_bytes = [] # np.zeros(self.n)
        flow.udps.n_bytes_counted = 0
        
        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        ''' '''
        remaining_bytes = self.n - flow.udps.n_bytes_counted
        if remaining_bytes >= 0 and packet.protocol in [6, 17]: # TCP or UDP only.
            amount_to_copy = min(remaining_bytes, packet.payload_size)
            if amount_to_copy == 0:
                return

            copied_binary_payload = self.get_payload_as_binary_pypacker(packet)[:amount_to_copy]
            flow.udps.n_bytes.extend(
                copied_binary_payload
            )
            flow.udps.n_bytes_counted += len(copied_binary_payload)

    def on_expire(self, flow):
        ''' '''
        '''
        Normalize to [0,1]: 
        flow.udps.n_bytes /= 255
        Optional cleanup: 
        del flow.udps.n_bytes_counted
        '''
        # Padding if necessary.
        if flow.udps.n_bytes_counted < self.n:
            remaining_bytes = self.n - flow.udps.n_bytes_counted
            flow.udps.n_bytes.extend(
                np.full(remaining_bytes, 0)
            )

    def get_payload_as_binary(self, packet):
        return packet.ip_packet[-packet.payload_size:]
    
    def get_payload_as_binary_scapy(self, packet):
        '''
        Older versions of NFStream (lower than 6.1) has problems with 
        detection the correct payload size of ipv6 packets.
        This function is here as a fallback in case of problems in future
        versions.

        in 6.4.2 and 6.4.3 there is a bug with wrong transport_size, also
        NFStream does not detect ethernet padding.
        '''
        ip_version = packet.ip_version
        if ip_version == 4:
            scapy_packet = IP(packet.ip_packet)
        elif ip_version == 6:
            scapy_packet = IPv6(packet.ip_packet)

        return raw(scapy_packet.payload.payload)
    
    def get_payload_as_binary_pypacker(self, packet):
        '''
        Scapy has a bug with correctly dissecting SNMP payload.
        '''
        ip_version = packet.ip_version
        if ip_version == 4:
            pypacker_packet = ip.IP(packet.ip_packet)
        elif ip_version == 6:
            pypacker_packet = ip6.IP6(packet.ip_packet)

        return pypacker_packet.upper_layer.body_bytes

    @staticmethod
    def preprocess(dataframe: pd.DataFrame):
        ''' 
        Preprocessing method for the n_bytes features.
        Converting 'udps.n_bytes' column from str to list.
        '''
        # validate
        assert 'udps.n_bytes' in dataframe.columns, "Column 'udps.n_bytes' not found."
        assert isinstance(dataframe['udps.n_bytes'].iloc[0], str), "Values in column 'udps.n_bytes' are already processed."
        
        dataframe['udps.n_bytes'] = dataframe['udps.n_bytes'].apply(ast.literal_eval)
        
        
