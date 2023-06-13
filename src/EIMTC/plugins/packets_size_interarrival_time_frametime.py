from runstats import *
from nfstream import NFPlugin
import numpy as np

class Packets_size_and_interarrival_time(NFPlugin):
    ''' Packets_size_and_interarrival_time |
    Extracts statistics of packet size (raw) and inter-arrival time (ms).
    
    Feature outputs:
        Statistics of packet size and IAT of the first 'n_packets' packets of the flow.
        
        Name Format:
            udps.packets_[FEATURE]_[STAT]
        
        Statistics (STAT) Names:
            - max
            - min
            - mean
            - stddev
            - skewness
            - variance
            - kurtosis
            - sum
            - first_quartile
            - second_quartile
            - third_quartile
            
        Feature Names:
            - size
            - interarrival_time
    
    Paper: 
        "Deep Learning for Network Traffic Classification".
    
        By:
            - Niloofar Bayat.
            - Weston Jackson.
            - Derrick Liu.
            
            Columbia University.
    
    Contribution Requests:
        1. Optimize median calculations by using histogram (if possible)
        
    '''
    def __init__(self, flow_time=None):
        '''
        Args:
            `flow_time` (int): The number of miliseconds to process the flow. If None then the whole flow will be processed.        
        '''
        self.flow_time = flow_time
    
    def on_init(self, packet, flow):
        ''' '''
        flow.udps.packets_size = list()
        flow.udps.packets_interarrival_time = list()
        self.on_update(packet,flow)

    def on_update(self, packet, flow):
        ''' '''
        if self.flow_time is not None and (packet.time - flow.bidirectional_first_seen_ms) > self.flow_time:
            return
        flow.udps.packets_size.append(packet.raw_size)
        flow.udps.packets_interarrival_time.append(packet.delta_time)

    def on_expire(self, flow):
        ''' '''
        packets_size_statistics = Statistics(flow.udps.packets_size)
        packets_interarrival_time_statistics = Statistics(flow.udps.packets_interarrival_time)

        #Packets Size Statistical
        packets_size_Q1,packets_size_Q2,packets_size_Q3 = quartile(np.array(flow.udps.packets_size))
        flow.udps.packets_size_min = packets_size_statistics.minimum() if packets_size_statistics._count > 0 else 0
        flow.udps.packets_size_max = packets_size_statistics.maximum() if packets_size_statistics._count > 0 else 0
        flow.udps.packets_size_stddev = packets_size_statistics.stddev() if packets_size_statistics._count >= 2 else 0
        flow.udps.packets_size_first_quartile = packets_size_Q1
        flow.udps.packets_size_second_quartile = packets_size_Q2
        flow.udps.packets_size_third_quartile = packets_size_Q3
        flow.udps.packets_size_mean = packets_size_statistics.mean()
        flow.udps.packets_size_median_absoulte_deviation = median_absolute_deviation(np.array(flow.udps.packets_size))
        flow.udps.packets_size_variance = packets_size_statistics.variance() if packets_size_statistics._count >= 2 else 0
        flow.udps.packets_size_skewness = packets_size_statistics.skewness() if flow.udps.packets_size_stddev != 0 else 0
        flow.udps.packets_size_kurtosis = packets_size_statistics.kurtosis() if flow.udps.packets_size_stddev != 0 else 0
        flow.udps.packets_size_sum = sum(flow.udps.packets_size)
        
        #Packets Interarrival Time Statistical
        packets_interarrival_time_Q1,packets_interarrival_time_Q2,packets_interarrival_time_Q3 = quartile(np.array(flow.udps.packets_interarrival_time))
        flow.udps.packets_interarrival_time_min = packets_interarrival_time_statistics.minimum() if packets_interarrival_time_statistics._count > 0 else 0
        flow.udps.packets_interarrival_time_max = packets_interarrival_time_statistics.maximum() if packets_interarrival_time_statistics._count > 0 else 0
        flow.udps.packets_interarrival_time_stddev = packets_interarrival_time_statistics.stddev() if packets_interarrival_time_statistics._count >= 2 else 0
        flow.udps.packets_interarrival_time_first_quartile = packets_interarrival_time_Q1
        flow.udps.packets_interarrival_time_second_quartile = packets_interarrival_time_Q2
        flow.udps.packets_interarrival_time_third_quartile = packets_interarrival_time_Q3
        flow.udps.packets_interarrival_time_mean = packets_interarrival_time_statistics.mean()
        flow.udps.packets_interarrival_time_median_absoulte_deviation = median_absolute_deviation(np.array(flow.udps.packets_interarrival_time))
        flow.udps.packets_interarrival_time_variance = packets_interarrival_time_statistics.variance() if packets_interarrival_time_statistics._count >= 2 else 0
        flow.udps.packets_interarrival_time_skewness = packets_interarrival_time_statistics.skewness() if flow.udps.packets_interarrival_time_stddev != 0 else 0
        flow.udps.packets_interarrival_time_kurtosis = packets_interarrival_time_statistics.kurtosis() if flow.udps.packets_interarrival_time_stddev != 0 else 0
        flow.udps.packets_interarrival_time_sum = sum(flow.udps.packets_interarrival_time)

def median_absolute_deviation(arr):
    return np.median(np.absolute(arr-np.median(arr)))

def quartile(arr):
    sorted_arr = np.sort(arr)
    median = sorted_median(sorted_arr)
    sorted_len = len(sorted_arr)
    half = int(sorted_len/2)
    if sorted_len % 2 == 0:
        return sorted_median(sorted_arr[0:half]),median,sorted_median(sorted_arr[half:sorted_len])
    else:
        return sorted_median(sorted_arr[0:half+1]),median,sorted_median(sorted_arr[half:sorted_len])

def sorted_median(sorted_arr):
    arr_len = len(sorted_arr)
    half = int(arr_len/2)
    if arr_len % 2 == 0:
        return (sorted_arr[half-1]+sorted_arr[half])/2
    else:
        return sorted_arr[half]