from nfstream import NFPlugin
import numpy as np


class SimpleTIG(NFPlugin):
    ''' 
    # SimpleTIG
    ## Description:
    A simple Traffic interaction Graph (TIG) feature extractor.
    
    From each packet the plugin extracts the packet size and the packet direction,
    the final feature is a signed packet size (neg size for src2dst, pos size for dst2src).
    
    output features: 
    1. `udps.simple_tig_adj`: Adjacency matrix of the graph. Shape of (`n_packets`, `n_packets`). 
    2. `udps.simple_tig_features`: Node features, a signed packet size. Shape of (`n_packets`, 1).
        
    ## Paper:
    "Accurate Decentralized Application Identification via Encrypted Traffic Analysis Using Graph Neural Networks,"
    ### By:
    - Meng Shen, 
    - Jinpeng Zhang, 
    - Liehuang Zhu, 
    - Ke Xu, 
    - Xiaojiang Du.
    '''
    def __init__(self, n_packets=10, size_type='raw'):
        self.n_packets = n_packets
        self.size_type = size_type
        
    def on_init(self, packet, flow):
        flow.udps.simple_tig_values = []
        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        if flow.bidirectional_packets > self.n_packets:
            return
        
        size = self._packet_size_by_type(packet, self.size_type)
        dir = -1 if packet.direction == 0 else 1
        flow.udps.simple_tig_values.append(size * dir)
        
    def on_expire(self, flow):
        padding_amount_required = self.n_packets - len(flow.udps.simple_tig_values)
        graph = generate_simple_TIG(flow.udps.simple_tig_values, padding=padding_amount_required)
            
        flow.udps.simple_tig_adj = graph.adj.tolist()
        flow.udps.simple_tig_features = graph.features.tolist()
        
        del flow.udps.simple_tig_values
        
    def _packet_size_by_type(self, packet, size_type):
        if size_type == 'raw':
            return packet.raw_size
        elif size_type == 'ip':
            return packet.ip_size
        elif size_type == 'transport':
            return packet.transport_size
        elif size_type == 'payload':
            return packet.payload_size
        
        return None


def generate_simple_TIG(values, padding=0):
    nodes = len(values) + padding
    graph = Graph(
        nodes, 
        features=np.concatenate([
            np.array(values).reshape(-1, 1), 
            np.zeros(padding).reshape(-1, 1)
        ])
    )
    bursts = get_bursts(values)
    
    for b in bursts:
        graph.connect_inner_burst(b)
    
    if len(bursts) > 1:
        for b1, b2 in zip(bursts[:-1], bursts[1:]):
            graph.connect_bursts(b1, b2)
    
    return graph


def get_bursts(data, ids=None):
    if ids == None:
        ids = np.arange(len(data))
    bursts = []
    last_sign = np.sign(data[0])
    last_id_idx = 0
    burst = []
    for val in data:
        if np.sign(val) != last_sign:
            bursts.append(Burst(burst, ids[last_id_idx:last_id_idx+len(burst)]))
            last_id_idx += len(burst)
            burst = []
        burst.append(val)
        last_sign = np.sign(val)
    bursts.append(Burst(burst, ids[last_id_idx:last_id_idx+len(burst)]))
        
    return bursts


class Graph:
    def __init__(self, n, features=None, f=None):
        self.adj = np.zeros((n, n))
        if features is not None:
            self.features = features
        else:
            self.features = np.zeros((n, f))
    
    def connect(self, v1, v2):
        self.adj[v1, v2] = 1
        self.adj[v2, v1] = 1
        
    def connect_inner_burst(self, burst):
        if burst.length() == 1:
            return
        
        for node_id1, node_id2 in zip(burst.ids[:-1], burst.ids[1:]):
            self.connect(node_id1, node_id2)
            
    def connect_bursts(self, burst1, burst2):
        self.connect(burst1.first(), burst2.first())
        if burst1.length() == 1 and burst2.length() > 1:
            self.connect(burst1.first(), burst2.last())
        elif burst1.length() > 1 and burst2.length() == 1:
            self.connect(burst1.last(), burst2.first())
        else:
            self.connect(burst1.last(), burst2.last())


class Burst:
    def __init__(self, values, ids):
        self.values = values
        self.ids = ids
        
    def length(self):
        return len(self.values)
    
    def first(self):
        return self.ids[0]
    
    def last(self):
        return self.ids[-1]
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return str(list(zip(self.values, self.ids)))