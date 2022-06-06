from math import e
from nfstream import NFStreamer, NFPlugin
import numpy as np
from scapy.all import IP, TCP
from runstats import *

class STNN(NFPlugin):
    '''
    wip
    '''
    def __init__(self,n_packets=32):
        self.n_packets = n_packets

    def on_init(self, packet, flow):
        
        flow.udps.bidirectional_addtional_info = np.full(4,0)
        flow.udps.bidirectional_packets_iat_stats = Statistics()
        flow.udps.bidirectional_packets_size_stats = Statistics()

        flow.udps.src2dst_addtional_info = np.full(4,0)
        flow.udps.src2dst_packets_iat_stats = Statistics()
        flow.udps.src2dst_packets_size_stats = Statistics()

        flow.udps.dst2src_addtional_info = np.full(4,0)
        flow.udps.dst2src_packets_iat_stats = Statistics()
        flow.udps.dst2src_packets_size_stats = Statistics()

        flow.udps.handshake_addtional_info = np.full(4,0)
        flow.udps.handshake_packets_iat_stats = Statistics()
        flow.udps.handshake_packets_size_stats = Statistics()
        flow.udps.handshake_packets_duration = 0

        flow.udps.data_addtional_info = np.full(4,0)
        flow.udps.data_packets_iat_stats = Statistics()
        flow.udps.data_packets_size_stats = Statistics()


        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        if flow.bidirectional_packets <= self.n_packets:
            flow.udps.bidirectional_packets_iat_stats.push(packet.delta_time)
            flow.udps.bidirectional_packets_size_stats.push(packet.raw_size)

            if packet.direction == 0:
                flow.udps.src2dst_packets_iat_stats.push(packet.delta_time)
                flow.udps.src2dst_packets_size_stats.push(packet.raw_size)
            elif packet.direction == 1:
                flow.udps.dst2src_packets_iat_stats.push(packet.delta_time)
                flow.udps.dst2src_packets_size_stats.push(packet.raw_size)
            if packet.protocol == 6 and packet.syn == True:
                flow.udps.handshake_packets_iat_stats.push(packet.delta_time)
                flow.udps.handshake_packets_size_stats.push(packet.raw_size)
                flow.udps.handshake_addtional_info[0] += 1
                flow.udps.handshake_addtional_info[1] += packet.raw_size
                flow.udps.handshake_packets_duration = flow.bidirectional_duration_ms
            if packet.protocol != 6 or packet.syn == False:
                flow.udps.data_packets_iat_stats.push(packet.delta_time)
                flow.udps.data_packets_size_stats.push(packet.raw_size)
        
        



    def on_expire(self, flow):
        matrix = np.empty((5,14))
        bidirectional_duration = 1 if flow.bidirectional_duration_ms == 0 else flow.bidirectional_duration_ms/1000
        flow.udps.bidirectional_addtional_info = [flow.bidirectional_packets,flow.bidirectional_bytes,flow.bidirectional_packets/bidirectional_duration,flow.bidirectional_bytes/bidirectional_duration]
        src2dst_duration = 1 if flow.src2dst_duration_ms == 0 else flow.src2dst_duration_ms/1000
        flow.udps.src2dst_addtional_info = [flow.src2dst_packets,flow.src2dst_bytes,flow.src2dst_packets/src2dst_duration,flow.src2dst_bytes/src2dst_duration]
        dst2src_duration = 1 if flow.dst2src_duration_ms == 0 else flow.dst2src_duration_ms/1000
        flow.udps.dst2src_addtional_info = [flow.dst2src_packets,flow.dst2src_bytes,flow.dst2src_packets/dst2src_duration,flow.dst2src_bytes/dst2src_duration]
        handshake_duration = flow.udps.handshake_packets_duration
        flow.udps.handshake_packets_duration = 1 if flow.udps.handshake_packets_duration == 0 else flow.udps.handshake_packets_duration/1000
        flow.udps.handshake_addtional_info[2:] = [flow.udps.handshake_addtional_info[0]/flow.udps.handshake_packets_duration,flow.udps.handshake_addtional_info[1]/flow.udps.handshake_packets_duration]
        data_packets = flow.bidirectional_packets-flow.udps.handshake_addtional_info[0]
        data_bytes = flow.bidirectional_bytes-flow.udps.handshake_addtional_info[1]
        data_duration = 1 if flow.bidirectional_duration_ms-handshake_duration == 0 else (flow.bidirectional_duration_ms-handshake_duration)/1000
        flow.udps.data_addtional_info = [data_packets,data_bytes,data_packets/data_duration,data_bytes/data_duration]
        stnn_objects = [
            (flow.udps.bidirectional_addtional_info,flow.udps.bidirectional_packets_iat_stats,flow.udps.bidirectional_packets_size_stats),
            (flow.udps.src2dst_addtional_info,flow.udps.src2dst_packets_iat_stats,flow.udps.src2dst_packets_size_stats),
            (flow.udps.dst2src_addtional_info,flow.udps.dst2src_packets_iat_stats,flow.udps.dst2src_packets_size_stats),
            (flow.udps.handshake_addtional_info,flow.udps.handshake_packets_iat_stats,flow.udps.handshake_packets_size_stats),
            (flow.udps.data_addtional_info,flow.udps.data_packets_iat_stats,flow.udps.data_packets_size_stats),
        ]

        for i,(add_info,iat_stats,size_stats) in enumerate(stnn_objects):
            matrix[i,0] = iat_stats.minimum() if iat_stats._count > 0 else 0
            matrix[i,1] = iat_stats.maximum() if iat_stats._count > 0 else 0
            matrix[i,2] = iat_stats.mean()
            matrix[i,3] = iat_stats.stddev() if iat_stats._count >= 2 else 0
            matrix[i,4] = iat_stats.skewness() if matrix[i,3] != 0 else 0
            matrix[i,5] = size_stats.minimum() if size_stats._count > 0 else 0
            matrix[i,6] = size_stats.maximum() if size_stats._count > 0 else 0
            matrix[i,7] = size_stats.mean()
            matrix[i,8] = size_stats.stddev() if size_stats._count >= 2 else 0
            matrix[i,9] = size_stats.skewness() if matrix[i,8] != 0 else 0
            matrix[i,10:] = add_info
            
        del flow.udps.bidirectional_addtional_info
        del flow.udps.bidirectional_packets_iat_stats
        del flow.udps.bidirectional_packets_size_stats
        del flow.udps.src2dst_addtional_info
        del flow.udps.src2dst_packets_iat_stats
        del flow.udps.src2dst_packets_size_stats
        del flow.udps.dst2src_addtional_info
        del flow.udps.dst2src_packets_iat_stats
        del flow.udps.dst2src_packets_size_stats
        del flow.udps.handshake_addtional_info
        del flow.udps.handshake_packets_iat_stats
        del flow.udps.handshake_packets_size_stats
        del flow.udps.data_addtional_info
        del flow.udps.data_packets_iat_stats
        del flow.udps.data_packets_size_stats

        flow.udps.stnn_image = [list(i) for i in matrix.astype(np.float32)]
        
        
    @staticmethod
    def preprocess(dataframe):
        ''' 
        Preprocessing method for the STNN features.
        Converting 'udps.stnn_image' column from str to 2D-list.
        '''
        import ast
        # validate
        assert 'udps.stnn_image' in dataframe.columns, "Column 'udps.stnn_image' not found."
        assert isinstance(dataframe['udps.stnn_image'].iloc[0], str), "Values in column 'udps.stnn_image' are already processed."
        
        dataframe['udps.stnn_image'] = dataframe['udps.stnn_image'].apply(ast.literal_eval)