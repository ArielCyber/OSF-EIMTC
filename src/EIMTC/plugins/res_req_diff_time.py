from EIMTC.stats.stats import IterableStats
from nfstream import NFPlugin
import numpy as np # for bytes distribution

class ResReqDiffTime(NFPlugin):
    ''' ResReqDiffTime | 
    Statistics of delta time between upload packets to download packets.
    For example, if there are 3 consequtive packets at time t1 going from src -> dst, and then the next packet is
    from the other direction, dst -> src, at tune t2 then the time calculation is the diff between the first upload packet
    to the first download packet hence, t2 -t1. This process repeats to get a list of such values. The plugin then extracts
    statistics on the series of time values.
    
    Output Features:
        udps.req_res_time_diff: (list) The time values of flow direction changes.
        udps.min_req_res_time_diff: (float)
        udps.max_req_res_time_diff: (float)
        udps.mean_req_res_time_diff: (float)
        udps.stddev_req_res_time_diff: (float)
        udps.variance_req_res_time_diff: (float)
        udps.coeff_of_var_req_res_time_diff: (float)
        udps.skew_from_median_req_res_time_diff: (float)
        
        Name Format:
            udps.[STAT]_req_res_time_diff
        
        Statistics (STAT) Names:
            - max
            - min
            - mean
            - stddev
            - variance
            - coeff_of_var
            - skew_from_median
    '''
    def __init__(self, **kwargs):
        ''' '''
        super().__init__(**kwargs)

    def on_init(self, packet, flow):
        ''' '''
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
        ''' '''
        if packet.direction != flow.udps.current_flow_direction:
            flow.udps.req_res_time_diff.append(packet.time - flow.udps.current_flow_direction_timestamp)
            flow.udps.current_flow_direction = packet.direction
            flow.udps.current_flow_direction_timestamp = packet.time

    def on_expire(self, flow): 
        ''' '''
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



