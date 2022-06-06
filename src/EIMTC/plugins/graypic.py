from nfstream import NFPlugin
import numpy as np
from PIL import Image
import os


class GrayPic1(NFPlugin):
    '''
    Description:
        Produces two gray-scaled image/picture, first of size 16x40 (IAT to packet-sizes),
        and the second of size 30x40 (burst/clump time to burst/clump size in bytes).
        data is extracted from the 1024-packet windows of bi-flow (default), this number can be configured.
    
    Paper:
        "Fingerprinting encrypted network traffic types using machine learning"
    By:
        Sam Leroux, 
        Steven Bohez, 
        Pieter-Jan Maenhaut, 
        Nathan Meheus, 
        Pieter Simoens, 
        Bart Dhoedt.
        - Department of Information Technology, IDLab, Ghent University - imec
    Source:
        https://biblio.ugent.be/publication/8559975/file/8559977.pdf
    '''

    def __init__(self, save_path, n_first_packets=1024, **kwargs):
        super().__init__(**kwargs)
        self.save_path = save_path
        self.n_first_packets = n_first_packets

    def on_init(self, packet, flow):
        flow.udps.graypic1_iat2packetsizes     = np.zeros((40, 16), dtype=np.uint32)
        flow.udps.graypic1_bursttime2burstsize = np.zeros((40, 30), dtype=np.uint32)
        flow.udps.graypic1_previous_packet_time = packet.time
        flow.udps.graypic1_packets = 0
        flow.udps.graypic1_pic_count = 0
        flow.udps.graypic1_burst_size = 0 # in bytes
        flow.udps.graypic1_burst_direction = packet.direction 
        flow.udps.graypic1_burst_start_time = packet.time
        flow.udps.graypic1_burst_end_time = packet.time
        
        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        flow.udps.graypic1_packets += 1
        self._handle_iat2packetsizes(packet, flow)
        self._handle_bursttime2burstsize(packet, flow)
        flow.udps.graypic1_previous_packet_time = packet.time
        
        if flow.udps.graypic1_packets == self.n_first_packets:
            self._handle_iat2packetsizes_finalize(packet, flow)
            self._handle_bursttime2burstsize_finalize(packet, flow)
            flow.udps.graypic1_packets = 0
            flow.udps.graypic1_pic_count += 1
        
    def on_expire(self, flow):
        # cleanup
        del flow.udps.graypic1_iat2packetsizes     
        del flow.udps.graypic1_bursttime2burstsize 
        del flow.udps.graypic1_previous_packet_time
        del flow.udps.graypic1_packets
        del flow.udps.graypic1_pic_count
        del flow.udps.graypic1_burst_size
        del flow.udps.graypic1_burst_direction 
        del flow.udps.graypic1_burst_start_time
        del flow.udps.graypic1_burst_end_time

    def _handle_iat2packetsizes(self, packet, flow):
        scaled_size = int(np.log(packet.ip_size)) * (1 if packet.direction==0 else -1)
        if packet.time - flow.udps.graypic1_previous_packet_time != 0:
            scaled_interarrival_time = int(np.log(packet.time - flow.udps.graypic1_previous_packet_time)) * (1 if packet.direction==0 else -1)
        else:
            scaled_interarrival_time = 0
        flow.udps.graypic1_iat2packetsizes[20+scaled_interarrival_time, 8+scaled_size] += 1
        
       
    def _handle_iat2packetsizes_finalize(self, packet, flow):
        # save and stuff
        flow.udps.graypic1_iat2packetsizes = ((flow.udps.graypic1_iat2packetsizes/np.sum(flow.udps.graypic1_iat2packetsizes))*255).astype(np.uint8)
        flow.udps.graypic1_iat2packetsizes = np.flip(flow.udps.graypic1_iat2packetsizes, axis=0)
        flow.udps.graypic1_iat2packetsizes = 255-flow.udps.graypic1_iat2packetsizes # for clarity/debug
        img = Image.fromarray(flow.udps.graypic1_iat2packetsizes, 'L') # L = 8bit black and white (gray scale)
        img.save(os.path.join(self.save_path,
                        '-'.join(['graypic1',str(flow.udps.graypic1_pic_count), flow.src_ip, str(flow.src_port), flow.dst_ip, str(flow.dst_port), str(flow.protocol)])
                        + '.png'))
        print('saved:', os.path.join(self.save_path,
                        '-'.join(['graypic1',str(flow.udps.graypic1_pic_count), flow.src_ip, str(flow.src_port), flow.dst_ip, str(flow.dst_port), str(flow.protocol)])
                        + '.png'))
        
        flow.udps.graypic1_iat2packetsizes = np.zeros((40, 16), dtype=np.uint32)
            
    def _handle_bursttime2burstsize(self, packet, flow):
        if packet.payload_size == 0: # skip ACK packets and empty payload packets
            return
        
        if flow.udps.graypic1_burst_direction == -1:
            flow.udps.graypic1_burst_direction = packet.direction 
            flow.udps.graypic1_burst_start_time = packet.time
            
        if packet.direction != flow.udps.graypic1_burst_direction:
            if flow.udps.graypic1_burst_end_time - flow.udps.graypic1_burst_start_time != 0:
                scaled_burst_duration = int(np.log(flow.udps.graypic1_burst_end_time - flow.udps.graypic1_burst_start_time)) * (1 if packet.direction==0 else -1) # ms 
            else:
                scaled_burst_duration = 0
            if flow.udps.graypic1_burst_size != 0:
                scaled_burst_size = int(np.log(flow.udps.graypic1_burst_size)) * (1 if packet.direction==0 else -1) # in bytes
            else:
                scaled_burst_size = 0
            flow.udps.graypic1_bursttime2burstsize[20+scaled_burst_duration, 15+scaled_burst_size] += 1
            
            flow.udps.graypic1_burst_start_time = packet.time
            flow.udps.graypic1_burst_end_time   = packet.time
            flow.udps.graypic1_burst_size       = packet.ip_size
            flow.udps.graypic1_burst_direction  = packet.direction
        else:
            flow.udps.graypic1_burst_end_time = packet.time
            flow.udps.graypic1_burst_size    += packet.ip_size
        
              
    def _handle_bursttime2burstsize_finalize(self, packet, flow):
        # save and stuff
        flow.udps.graypic1_bursttime2burstsize = ((flow.udps.graypic1_bursttime2burstsize/np.sum(flow.udps.graypic1_bursttime2burstsize))*255).astype(np.uint8)
        flow.udps.graypic1_bursttime2burstsize = np.flip(flow.udps.graypic1_bursttime2burstsize, axis=0)
        flow.udps.graypic1_bursttime2burstsize = 255-flow.udps.graypic1_bursttime2burstsize # for clarity/debug
        img = Image.fromarray(flow.udps.graypic1_bursttime2burstsize, 'L') # L = 8bit black and white (gray scale)
        img.save(os.path.join(self.save_path,
                        '-'.join(['graypic1', 'burst',str(flow.udps.graypic1_pic_count), flow.src_ip, str(flow.src_port), flow.dst_ip, str(flow.dst_port), str(flow.protocol)])
                        + '.png'))
        print('saved:', os.path.join(self.save_path,
                        '-'.join(['graypic1', 'burst',str(flow.udps.graypic1_pic_count), flow.src_ip, str(flow.src_port), flow.dst_ip, str(flow.dst_port), str(flow.protocol)])
                        + '.png'))
        
       
        flow.udps.graypic1_bursttime2burstsize = np.zeros((40, 30), dtype=np.uint32)
        flow.udps.graypic1_burst_size = 0 # in bytes
        flow.udps.graypic1_burst_direction = -1