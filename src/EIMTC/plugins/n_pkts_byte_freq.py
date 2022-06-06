# used for byte frequency analysis

from ..stats.stats import IterableStats, WeightedIterableStats
from nfstream import NFPlugin
import numpy as np # for bytes distribution

class NPacketsByteFrequency(NFPlugin):
    def __init__(self, n_first_packets = 0, **kwargs):
        '''
        Params:
            n_first_packets: the byte distribution will be taken
            from the n first packets only (bidirectional), if n_first_packets=0 then
            the byte distribution will taken from all packets in the flow.
        '''
        super().__init__(**kwargs)
        self.n_first_packets = n_first_packets

    def on_init(self, packet, flow):
        '''
        on_init(self, packet, flow): Method called at flow creation.
        '''
        
        flow.udps.n_packets_byte_frequency_value = self.n_first_packets
        flow.udps.bidirectional_n_packets_byte_frequency = np.zeros(256) # of ip payload onwards
        flow.udps.src2dst_n_packets_byte_frequency = np.zeros(256) # of ip payload onwards
        flow.udps.dst2src_n_packets_byte_frequency = np.zeros(256) # of ip payload onwards
      
        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        if self.n_first_packets == 0 or flow.bidirectional_packets <= self.n_first_packets:
            if packet.direction == 0: # src -> dst
                self._add_payload_bytes_frequency(packet.ip_packet, flow.udps.src2dst_n_packets_byte_frequency)
            else: # dst -> src
                self._add_payload_bytes_frequency(packet.ip_packet, flow.udps.dst2src_n_packets_byte_frequency)
            
            # compute/update bidirectional.
            self._add_payload_bytes_frequency(packet.ip_packet, flow.udps.bidirectional_n_packets_byte_frequency)

    def on_expire(self, flow):
        '''
        Todo: zero and nan checks.
        '''
        # Normalize frequencies to get distribution
        bidirectional_n_packets_byte_distribution = flow.udps.bidirectional_n_packets_byte_frequency # / np.sum(flow.udps.bidirectional_n_packets_byte_frequency)
        src2dst_n_packets_byte_distribution       = flow.udps.src2dst_n_packets_byte_frequency # / np.sum(flow.udps.src2dst_n_packets_byte_frequency)
        dst2src_n_packets_byte_distribution       = flow.udps.dst2src_n_packets_byte_frequency # / np.sum(flow.udps.dst2src_n_packets_byte_frequency)
        # Compute statistical features
        # bidirectional
        bidirectional_stats = WeightedIterableStats(np.arange(0,256), bidirectional_n_packets_byte_distribution)
        flow.udps.bidirectional_mean_n_packets_byte_distribution             = bidirectional_stats.average()
        flow.udps.bidirectional_stdev_n_packets_byte_distribution            = bidirectional_stats.std_deviation()
        flow.udps.bidirectional_median_n_packets_byte_distribution           = bidirectional_stats.median()
        flow.udps.bidirectional_variance_n_packets_byte_distribution         = bidirectional_stats.variance()
        flow.udps.bidirectional_coeff_of_var_n_packets_byte_distribution     = bidirectional_stats.coeff_of_variation()
        flow.udps.bidirectional_skew_from_median_n_packets_byte_distribution = bidirectional_stats.skew_from_median()
        # src -> dst
        src2dst_stats = WeightedIterableStats(np.arange(0,256), src2dst_n_packets_byte_distribution)
        flow.udps.src2dst_mean_n_packets_byte_distribution             = src2dst_stats.average()
        flow.udps.src2dst_stdev_n_packets_byte_distribution            = src2dst_stats.std_deviation()
        flow.udps.src2dst_median_n_packets_byte_distribution           = src2dst_stats.median()
        flow.udps.src2dst_variance_n_packets_byte_distribution         = src2dst_stats.variance()
        flow.udps.src2dst_coeff_of_var_n_packets_byte_distribution     = src2dst_stats.coeff_of_variation()
        flow.udps.src2dst_skew_from_median_n_packets_byte_distribution = src2dst_stats.skew_from_median()
        # dst -> src
        dst2src_stats = WeightedIterableStats(np.arange(0,256), dst2src_n_packets_byte_distribution)
        flow.udps.dst2src_mean_n_packets_byte_distribution             = dst2src_stats.average()
        flow.udps.dst2src_stdev_n_packets_byte_distribution            = dst2src_stats.std_deviation()
        flow.udps.dst2src_median_n_packets_byte_distribution           = dst2src_stats.median()
        flow.udps.dst2src_variance_n_packets_byte_distribution         = dst2src_stats.variance()
        flow.udps.dst2src_coeff_of_var_n_packets_byte_distribution     = dst2src_stats.coeff_of_variation()
        flow.udps.dst2src_skew_from_median_n_packets_byte_distribution = dst2src_stats.skew_from_median()
        
        flow.udps.bidirectional_n_packets_byte_frequency = flow.udps.bidirectional_n_packets_byte_frequency.tolist() 
        flow.udps.src2dst_n_packets_byte_frequency = flow.udps.src2dst_n_packets_byte_frequency.tolist()
        flow.udps.dst2src_n_packets_byte_frequency = flow.udps.dst2src_n_packets_byte_frequency.tolist()
        # Cleanup
        

    def _add_payload_bytes_frequency(self, payload, container):
        payload_bytes_array = np.frombuffer(payload, dtype='B') # 'B' unsigned byte
        container[payload_bytes_array] += 1
