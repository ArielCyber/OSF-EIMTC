from ..stats.stats import IterableStats
from nfstream import NFPlugin


class PacketRelativeTime(NFPlugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_init(self, packet, flow):
        '''
        on_init(self, packet, flow): Method called at flow creation.
        '''
        # bidirectional
        flow.udps.bidirectional_packet_relative_times = list()
        flow.udps.bidirectional_min_packet_relative_times              = 0
        flow.udps.bidirectional_max_packet_relative_times              = 0
        flow.udps.bidirectional_mean_packet_relative_times             = 0
        flow.udps.bidirectional_stddev_packet_relative_times           = None
        flow.udps.bidirectional_variance_packet_relative_times         = None
        flow.udps.bidirectional_coeff_of_var_packet_relative_times     = None
        flow.udps.bidirectional_skew_from_median_packet_relative_times = None
        # src -> dst
        flow.udps.src2dst_packet_relative_times = list()
        flow.udps.src2dst_min_packet_relative_times              = 0
        flow.udps.src2dst_max_packet_relative_times              = 0
        flow.udps.src2dst_mean_packet_relative_times             = 0
        flow.udps.src2dst_stddev_packet_relative_times           = None
        flow.udps.src2dst_variance_packet_relative_times         = None
        flow.udps.src2dst_coeff_of_var_packet_relative_times     = None
        flow.udps.src2dst_skew_from_median_packet_relative_times = None
        # dst -> src
        flow.udps.dst2src_packet_relative_times = list()
        flow.udps.dst2src_min_packet_relative_times              = 0
        flow.udps.dst2src_max_packet_relative_times              = 0
        flow.udps.dst2src_mean_packet_relative_times             = 0
        flow.udps.dst2src_stddev_packet_relative_times           = None
        flow.udps.dst2src_variance_packet_relative_times         = None
        flow.udps.dst2src_coeff_of_var_packet_relative_times     = None
        flow.udps.dst2src_skew_from_median_packet_relative_times = None

        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        if packet.direction == 0: # src -> dst
            flow.udps.src2dst_packet_relative_times.append(packet.time
                                    - flow.bidirectional_first_seen_ms)
        elif packet.direction == 1:
            flow.udps.dst2src_packet_relative_times.append(packet.time
                                    - flow.bidirectional_first_seen_ms)
            
        flow.udps.bidirectional_packet_relative_times.append(packet.time
                                    - flow.bidirectional_first_seen_ms)

        
    def on_expire(self, flow):
        # bidirectional
        stats = IterableStats(flow.udps.bidirectional_packet_relative_times)
        flow.udps.bidirectional_min_packet_relative_times              = stats.min()
        flow.udps.bidirectional_max_packet_relative_times              = stats.max()
        flow.udps.bidirectional_mean_packet_relative_times             = stats.average()
        flow.udps.bidirectional_stddev_packet_relative_times           = stats.std_deviation()
        flow.udps.bidirectional_variance_packet_relative_times         = stats.variance()
        flow.udps.bidirectional_coeff_of_var_packet_relative_times     = stats.coeff_of_variation()
        flow.udps.bidirectional_skew_from_median_packet_relative_times = stats.skew_from_median()
        # src -> dst
        stats = IterableStats(flow.udps.src2dst_packet_relative_times)
        flow.udps.src2dst_min_packet_relative_times              = stats.min()
        flow.udps.src2dst_max_packet_relative_times              = stats.max()
        flow.udps.src2dst_mean_packet_relative_times             = stats.average()
        flow.udps.src2dst_stddev_packet_relative_times           = stats.std_deviation()
        flow.udps.src2dst_variance_packet_relative_times         = stats.variance()
        flow.udps.src2dst_coeff_of_var_packet_relative_times     = stats.coeff_of_variation()
        flow.udps.src2dst_skew_from_median_packet_relative_times = stats.skew_from_median()
        # dst -> src
        stats = IterableStats(flow.udps.dst2src_packet_relative_times)
        flow.udps.dst2src_min_packet_relative_times              = stats.min()
        flow.udps.dst2src_max_packet_relative_times              = stats.max()
        flow.udps.dst2src_mean_packet_relative_times             = stats.average()
        flow.udps.dst2src_stddev_packet_relative_times           = stats.std_deviation()
        flow.udps.dst2src_variance_packet_relative_times         = stats.variance()
        flow.udps.dst2src_coeff_of_var_packet_relative_times     = stats.coeff_of_variation()
        flow.udps.dst2src_skew_from_median_packet_relative_times = stats.skew_from_median()
