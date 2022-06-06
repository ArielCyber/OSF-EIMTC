from nfstream import NFPlugin
from PIL import Image
import numpy as np
import os

class FlowPic2019(NFPlugin):
    '''
    File name structure:
        flowpic-[flow_start_time_ms]-[src_ip]-[src_port]-[dst_ip]-[dst_port]-[protocol]-[direction].png
    
    '''
    def __init__(self, save_path, flow_direction=0, flow_active_time=30, image_dims=(1500, 1500), **kwargs):
        super().__init__(**kwargs)
        self.save_path = save_path
        self.flowpic_flow_direction = flow_direction # NOT USED AT THE MOMENT
        self.flow_active_time = flow_active_time
        self.image_dims = image_dims

    def on_init(self, packet, flow):
        flow.udps.src2dst_flowpic_image = np.zeros(self.image_dims, dtype=np.uint32)
        flow.udps.dst2src_flowpic_image = np.zeros(self.image_dims, dtype=np.uint32)
        
        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        if packet.ip_size == 0 or packet.ip_size > self.image_dims[0]:
            # discard
            return
        
        if packet.direction == 0: # src -> dst
            relative_time = packet.time \
                            - flow.src2dst_first_seen_ms
            flow.udps.src2dst_flowpic_image[packet.ip_size, self._scale_to(relative_time, 0, self.image_dims[1])] += 1
        else:
            relative_time = packet.time \
                            - flow.dst2src_first_seen_ms
            flow.udps.dst2src_flowpic_image[packet.ip_size, self._scale_to(relative_time, 0, self.image_dims[1])] += 1    
        
    def on_expire(self, flow):
        ## SRC -> DST
        # normalize all cells/pixels in the image to [0,255].
        #flow.udps.src2dst_flowpic_image = flow.udps.src2dst_flowpic_image * 255 / np.sum(flow.udps.src2dst_flowpic_image)
        # reverse the Y axis such that the higher you go, the higher the values.
        flow.udps.src2dst_flowpic_image = np.flip(flow.udps.src2dst_flowpic_image, axis=0) 
        
        # for clarity/debug:
        temp = np.copy(flow.udps.src2dst_flowpic_image)
        '''
        flow.udps.src2dst_flowpic_image[temp>0]  = 0
        flow.udps.src2dst_flowpic_image[temp==0] = 255
        flow.udps.src2dst_flowpic_image = flow.udps.src2dst_flowpic_image.astype(np.uint8)
        '''
        
        np.savez_compressed(os.path.join(
                    self.save_path,
                    '-'.join(['flowpic',str(flow.bidirectional_first_seen_ms), flow.src_ip, str(flow.src_port), flow.dst_ip, str(flow.dst_port), str(flow.protocol), 'src2dst'])
                ), 
                flowpic=flow.udps.src2dst_flowpic_image,)
        img = Image.fromarray(flow.udps.src2dst_flowpic_image , 'I') # L = 8bit black and white (gray scale)
        img.save(
            os.path.join(
                self.save_path,
                '-'.join(['flowpic',str(flow.bidirectional_first_seen_ms), flow.src_ip, str(flow.src_port), flow.dst_ip, str(flow.dst_port), str(flow.protocol), 'src2dst'])
                + '.png'))
        ## DST -> SRC
        # normalize all cells/pixels in the image to [0,255].
        #flow.udps.dst2src_flowpic_image = flow.udps.dst2src_flowpic_image * 255 / np.sum(flow.udps.dst2src_flowpic_image)
        # reverse the Y axis such that the higher you go, the higher the values.
        flow.udps.dst2src_flowpic_image = np.flip(flow.udps.dst2src_flowpic_image, axis=0) 
        
        # for clarity/debug:
        temp = np.copy(flow.udps.dst2src_flowpic_image)
        '''
        flow.udps.dst2src_flowpic_image[temp>0]  = 0
        flow.udps.dst2src_flowpic_image[temp==0] = 255
        flow.udps.dst2src_flowpic_image = flow.udps.dst2src_flowpic_image.astype(np.uint8)
        '''
        
        img = Image.fromarray(flow.udps.dst2src_flowpic_image , 'L') # L = 8bit black and white (gray scale)
        img.save(
            os.path.join(
                self.save_path,
                '-'.join(['flowpic',str(flow.bidirectional_first_seen_ms), flow.src_ip, str(flow.src_port), flow.dst_ip, str(flow.dst_port), str(flow.protocol), 'dst2src'])
                + '.png'))
        
        print(str(flow.bidirectional_first_seen_ms), np.sum(temp))
        
    def _scale_to(self, value_ms, min_value=0, max_value=1500):
        max_time_s = self.flow_active_time
        value_s = value_ms/1000
        return int(value_s*((max_value-min_value)/max_time_s))
    