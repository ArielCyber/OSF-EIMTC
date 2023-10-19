from nfstream import NFPlugin
import numpy as np
import os

class FlowPic(NFPlugin):
    '''FlowPic | An NxN histogram of packet sizes and relative times, represented as an image.
    
    Output Features:
        Since the FlowPics can get very big and hence consume a lot of memory,
        instead of outputting the features as a column in a CSV file the images are
        exported to npz files with the following naming scheme:
        flowpic-[flow_start_time_ms]-[src_ip]-[src_port]-[dst_ip]-[dst_port]-[protocol]-[direction].npz
        
        Each FlowPic is captured on a specific time frame/window/subflow, hence, a flow can be partitioned
        into multiple time frames. In such cases, multiple .npz files can be created.
        
        To load the .npz files into memory you can use the following:
        ```
        flowpic_sample = np.load(filepath)['flowpic']
        ```
    
    Paper:
        "FlowPic: Encrypted Internet Traffic Classification is as Easy as Image Recognition".

        By:
            - Tal Shapira.
            - Yuval Shavitt.
    
    '''
    def __init__(self, save_path, time_per_subflow=30, min_time_per_subflow=None, min_packets_per_subflow=10, image_dims=(1500, 1500), MTU=1500):
        '''
        Args:
            `save_path` (str): The directory to save the .npz files.
            `time_per_subflow` (int): Duration for each subflow or time frame/window (in seconds). Default: 30s.
            `min_time_per_subflow` (int): Minimum duration for a time frame to process (in seconds). Default: 5/6 * `time_per_subflow`
            `min_packets_per_subflow` (int): Minimum packets for a time frame to process. Default: 10.
            `image_dims` (int, int): FlowPic output image dimensions. Default: (1500,1500).
            `MTU` (int): The max packet size to process, packets with size larger than `MTU` will be ignored. Default: 1500.
        '''
        self.save_path = save_path
        self.time_per_subflow = time_per_subflow
        self.min_time_per_subflow = int(np.ceil(time_per_subflow - time_per_subflow*0.1666667)) if min_time_per_subflow == None else min_time_per_subflow
        self.min_packets_per_subflow = min_packets_per_subflow
        self.image_dims = image_dims
        self.mtu = MTU

    def on_init(self, packet, flow):
        ''' '''
        flow.udps.src2dst_flowpic_data = _FlowPicInnerPlugin(flow.src2dst_first_seen_ms, self.mtu)
        flow.udps.dst2src_flowpic_data = None
        
        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        ''' '''
        if packet.ip_size == 0 or packet.ip_size > self.image_dims[0]:
            # discard
            return

        if packet.direction == 0: # src -> dst
            if self.is_subflow_ended(flow.udps.src2dst_flowpic_data.start_time, packet.time, self.time_per_subflow):
                if flow.udps.dst2src_flowpic_data.count > self.min_packets_per_subflow:
                    self.save_histogram(flow.udps.src2dst_flowpic_data.on_expire(), 
                                        flow.udps.src2dst_flowpic_data.start_time, 
                                        packet.direction,
                                        flow)
                flow.udps.src2dst_flowpic_data = _FlowPicInnerPlugin(packet.time, self.mtu)
            flow.udps.src2dst_flowpic_data.on_update(packet)
        else:
            if flow.udps.dst2src_flowpic_data == None:
                flow.udps.dst2src_flowpic_data = _FlowPicInnerPlugin(flow.dst2src_first_seen_ms, self.mtu)
            if self.is_subflow_ended(flow.udps.dst2src_flowpic_data.start_time, packet.time, self.time_per_subflow):
                if flow.udps.dst2src_flowpic_data.count > self.min_packets_per_subflow:
                    self.save_histogram(flow.udps.dst2src_flowpic_data.on_expire(), 
                                        flow.udps.dst2src_flowpic_data.start_time, 
                                        packet.direction,
                                    flow)
                flow.udps.dst2src_flowpic_data = _FlowPicInnerPlugin(packet.time, self.mtu)
            flow.udps.dst2src_flowpic_data.on_update(packet)
        
    def on_expire(self, flow):
        ''' '''
        ## SRC -> DST
        if flow.src2dst_packets > 0 \
            and flow.udps.src2dst_flowpic_data.count > self.min_packets_per_subflow \
            and self.is_subflow_ended(flow.udps.src2dst_flowpic_data.start_time, flow.src2dst_last_seen_ms, self.min_time_per_subflow):
            self.save_histogram(flow.udps.src2dst_flowpic_data.on_expire(), 
                                flow.udps.src2dst_flowpic_data.start_time,
                                0,
                                flow)
        ## DST -> SRC
        if flow.dst2src_packets > 0 \
            and flow.udps.dst2src_flowpic_data.count > self.min_packets_per_subflow \
            and self.is_subflow_ended(flow.udps.dst2src_flowpic_data.start_time, flow.dst2src_last_seen_ms, self.min_time_per_subflow):
            self.save_histogram(flow.udps.dst2src_flowpic_data.on_expire(), 
                                flow.udps.dst2src_flowpic_data.start_time,
                                1,
                                flow)
            
        # cleanup
        del flow.udps.src2dst_flowpic_data
        del flow.udps.dst2src_flowpic_data

    def save_histogram(self, hist, subflow_start_time, direction, flow):
        np.savez_compressed(
            os.path.join(
                self.save_path,
                '-'.join(['flowpic',
                    str(subflow_start_time), 
                    flow.src_ip, 
                    str(flow.src_port), 
                    flow.dst_ip, 
                    str(flow.dst_port), 
                    str(flow.protocol), 
                    'src2dst' if direction==0 else 'dst2src']
                )
            ), 
            flowpic=hist
        )

    def is_subflow_ended(self, start_time_ms, current_time_ms, time_per_subflow_s):
        return (current_time_ms - start_time_ms)/1000 > time_per_subflow_s


class _FlowPicInnerPlugin:
    '''
    NFPlugin-Like class to handle multiple subflows (slices of flows by time)
    For example, 130s flow, with slices of 60s, has 3 subflows.
    
    Note: Unidirectional.
    '''
    def __init__(self, subflow_start_time, mtu) -> None:
        self.start_time = subflow_start_time
        self.sizes = []
        self.timestamps = []
        self.mtu = mtu
        self.count = 0
    
    def on_update(self, packet):
        self.count += 1
        relative_time_ms = packet.time \
                        - self.start_time
        relative_time_s = relative_time_ms / 1000
        self.sizes.append(packet.ip_size)
        self.timestamps.append(relative_time_s)
        
    def on_expire(self):
        return self._flow_2d_histogram(self.sizes, self.timestamps)
        
    def _flow_2d_histogram(self, sizes, ts):
        '''
        Original Author: Tal Shapira, 
        Note: With some modifications.
        '''
        ts_norm = ((np.array(ts) - ts[0]) / (ts[-1] - ts[0])) * self.mtu
        H, xedges, yedges = np.histogram2d(sizes, ts_norm, bins=(range(0, self.mtu + 1, 1), range(0, self.mtu + 1, 1)))

        return H.astype(np.uint16)
        
        
    
