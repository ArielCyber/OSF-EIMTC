from nfstream import NFPlugin
import numpy as np 


class MostFreqPayloadLenRatio(NFPlugin):
    '''MostFreqPayloadLenRatio | The ratio of number of packets with most freq payload len for direction X to the the total number of packets
    in direction X, for each direction x in {src2dst, dst2src}.
    
    Output Features:
        1. udps.src2dst_most_freq_payload_ratio: The frequency of the most frequent payload divided by the total number of uploaded packets. (float)
        2. udps.src2dst_most_freq_payload_len: The most frequent payload length/size of the uploaded packets. (float)
        3. udps.src2dst_payload_freq: Frequencies of payload lengths of the uploaded packets. (dict)
        4. udps.dst2src_most_freq_payload_ratio: The frequency of the most frequent payload divided by the total number of downloaded packets. (float)
        5. udps.dst2src_most_freq_payload_len: The most frequent payload length/size of the downloaded packets. (float)
        6. udps.dst2src_payload_freq = Frequencies of payload lengths of the downloaded packets. (dict)
    
    '''
    def __init__(self, **kwargs):
        ''' '''
        super().__init__(**kwargs)

    def on_init(self, packet, flow):
        ''' '''

        flow.udps.src2dst_most_freq_payload_ratio = 0
        flow.udps.src2dst_most_freq_payload_len   = None
        flow.udps.src2dst_payload_freq = dict()
        flow.udps.dst2src_most_freq_payload_ratio = 0
        flow.udps.dst2src_most_freq_payload_len   = None
        flow.udps.dst2src_payload_freq = dict()

        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        ''' '''
        if packet.direction == 0: # src2dst
            if packet.payload_size not in flow.udps.src2dst_payload_freq:
                flow.udps.src2dst_payload_freq[packet.payload_size] = 0
            flow.udps.src2dst_payload_freq[packet.payload_size] +=1
        else:
            if packet.payload_size not in flow.udps.dst2src_payload_freq:
                flow.udps.dst2src_payload_freq[packet.payload_size] = 0
            flow.udps.dst2src_payload_freq[packet.payload_size] +=1

    def on_expire(self, flow):
        ''' '''
        if flow.src2dst_packets != 0:
            freq_dict = flow.udps.src2dst_payload_freq
            most_freq_payload_freq = max(freq_dict.values())
            flow.udps.src2dst_most_freq_payload_len   = list(freq_dict.keys())[np.argmax(list(freq_dict.values()))]
            flow.udps.src2dst_most_freq_payload_ratio = most_freq_payload_freq / flow.src2dst_packets
        if flow.dst2src_packets != 0:
            freq_dict = flow.udps.dst2src_payload_freq
            most_freq_payload_freq = max(freq_dict.values())
            flow.udps.dst2src_most_freq_payload_len   = list(freq_dict.keys())[np.argmax(list(freq_dict.values()))]
            flow.udps.dst2src_most_freq_payload_ratio = most_freq_payload_freq / flow.dst2src_packets
