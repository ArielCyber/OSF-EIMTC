from nfstream import NFStreamer, NFPlugin
import numpy as np
from scapy.all import IP, IPv6, rdpcap, raw


class NBytesPerPacket(NFPlugin):
    ''' NBytesPerPacket | 
    Extracts the first n_bytes from each packet in the flow, the bytes are taken
    from the transport layer payload (L4). if the flow has less than n_bytes bytes,
    then the rest of the bytes are zero-valued.
        
    remove_empty_payload flag tells the plugin to not add empty payload packets such as acks in TCP.
    max_packets param determines the highest amount of packets to save/extract from the flow.
        
    Paper:
        "DeepMAL - Deep Learning Models for Malware Traffic Detection and Classification."
        
        By:
            - Gonzalo Marín. 
            - Pedro Casas.
            - Germán Capdehourat.
            
    '''
    def __init__(self, n=1024, remove_empty_payload=True, max_packets=None):
        '''
        Args:
            `n` (int): The number of bytes to extract from each packet.
            `remove_empty_payload` (bool): Ignore packets with empty payload. Default: True.
            `max_packets` (int): The number of packets to extract from.
        '''
        self.n = n
        self.remove_empty_payload = remove_empty_payload
        self.max_packets = max_packets
    
    def on_init(self, packet, flow):
        ''' '''
        flow.udps.n_bytes_value = self.n
        flow.udps.n_bytes_per_packet = np.zeros((self.max_packets,self.n))
        flow.udps.n_bytes_curr_packets = 0
        
        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        ''' '''
        if packet.payload_size == 0 and self.remove_empty_payload == True:
            return
        
        if self.max_packets is not None and flow.udps.n_bytes_curr_packets == self.max_packets:
            return
        
        amount_to_copy = min(self.n, packet.payload_size)
        if amount_to_copy == 0:
            flow.udps.n_bytes_curr_packets += 1
            return
        
        max_index_to_copy = -packet.payload_size+amount_to_copy if -packet.payload_size+amount_to_copy != 0 else None
        flow.udps.n_bytes_per_packet[flow.udps.n_bytes_curr_packets,:amount_to_copy] = np.frombuffer(self.get_payload_as_binary(packet, flow.ip_version)[-packet.payload_size:max_index_to_copy], dtype=np.uint8)
        flow.udps.n_bytes_curr_packets += 1
        
        
    def on_expire(self, flow):
        ''' '''
        flow.udps.n_bytes_per_packet /= 255
        flow.udps.n_bytes_per_packet = [list(i) for i in flow.udps.n_bytes_per_packet]
        #[int(i) for i in list(flow.udps.n_bytes_per_packet)]
        #flow.udps.n_bytes_per_packet = list(flow.udps.n_bytes_per_packet)

    def get_payload_as_binary(self, packet, ip_version):
        ''' '''
        if ip_version == 4:
            scapy_packet = IP(packet.ip_packet)
        elif ip_version == 6:
            scapy_packet = IPv6(packet.ip_packet)
        
        return raw(scapy_packet.payload.payload)
        