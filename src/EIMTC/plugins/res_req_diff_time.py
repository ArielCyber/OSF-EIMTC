from ..stats.stats import IterableStats
from nfstream import NFPlugin
import numpy as np # for bytes distribution

class ResReqDiffTime(NFPlugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_init(self, packet, flow):
        '''
        on_init(self, packet, flow): Method called at flow creation.
        '''
        flow.udps.req_res_time_diff = list() 
        flow.udps.current_flow_direction = 0 # 0 for forward, 1 for backward
        flow.udps.current_flow_direction_timestamp = packet.time
        flow.udps.min_req_res_time_diff = 0
        flow.udps.max_req_res_time_diff = 0
        flow.udps.mean_req_res_time_diff = 0
        flow.udps.stddev_req_res_time_diff = 0
        flow.udps.variance_req_res_time_diff = 0
        flow.udps.coeff_of_var_req_res_time_diff = 0
        flow.udps.skew_from_median_req_res_time_diff = 0

    def on_update(self, packet, flow):
        if packet.direction != flow.udps.current_flow_direction:
            flow.udps.req_res_time_diff.append(packet.time - flow.udps.current_flow_direction_timestamp)
            flow.udps.current_flow_direction = packet.direction
            flow.udps.current_flow_direction_timestamp = packet.time

    def on_expire(self, flow): 
        stats = IterableStats(flow.udps.req_res_time_diff)
        flow.udps.min_req_res_time_diff = stats.min()
        flow.udps.max_req_res_time_diff = stats.max()
        flow.udps.mean_req_res_time_diff = stats.average()
        flow.udps.median_req_res_time_diff = stats.median()
        flow.udps.stddev_req_res_time_diff = stats.std_deviation()
        flow.udps.variance_req_res_time_diff = stats.variance()
        flow.udps.coeff_of_var_req_res_time_diff = stats.coeff_of_variation()
        flow.udps.skew_from_median_req_res_time_diff = stats.skew_from_median()
        
        # Cleanup
        del flow.udps.current_flow_direction_timestamp
        del flow.udps.current_flow_direction



