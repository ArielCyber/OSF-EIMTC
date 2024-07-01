from nfstream import NFPlugin
import numpy as np
from runstats import *
from scapy.all import IP, IPv6, raw

class TGNN(NFPlugin):
    ''' TGNN | A simple graph feature extractor.

    From each packet the plugin extracts the packet bytes, packet inter-arrival time, packet payload length, packet length. Also extract the flow duration.
    The packets bytes are used as weight for the nodes of the graph, the packet inter-arrival time is used as weight for the edges of the graph,
    and payload length mean, payload length SD, packet length mean, packet length SD, and flow duration are the meta features of the graph.
    
    Why simple: The plugin doesnt support any packet/node feature customization.
    
    Output Features: 
        1. `udps.simple_tgnn_adj`: Adjacency matrix of the graph. Shape of (`n_packets`, `n_packets`). 
        2. `udps.simple_tgnn_vertcies_features`: Node features, the packet size. Shape of (`n_packets`, 1).
        3. `udps.simple_tgnn_edges_weights`: Node weight edges, the packet inter-arrival time. Shape of (edges, 1).
        4. `udps.simple_tgnn_meta_features`: Graph meta features, payload length mean, payload length SD, packet length mean, packet length SD, and flow duration. Shape of (5).
        
    Paper:
        "Flow-based Encrypted Network Traffic Classification with Graph Neural Networks."
        
        By:
            - Ting-Li Huoh, 
            - Yan Luo, 
            - Peilong Li, 
            - Tong Zhang.
    '''
    def __init__(self, n_packets=5, MTU=1500):
        '''
        Args:
            `n_packets` (int): The number of packets to process per flow.
                flows with less than the desired `n_packets` will be padded with 
                unconnected zero-valued nodes to match `n_packets`.
        '''
        self.n_packets = n_packets
        self.MTU = MTU
    
    def on_init(self, packet, flow):
        '''
        on_init
        '''
        flow.udps.simple_tgnn_nodes_weight = np.zeros((self.n_packets,self.MTU))
        flow.udps.simple_tgnn_timestamp = np.zeros((self.n_packets))
        flow.udps.simple_tgnn_payload_length = Statistics()
        flow.udps.simple_tgnn_packet_length = Statistics()

        flow.udps.simple_tgnn_nodes_weight_no_norm = np.zeros((self.n_packets,self.MTU))
        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        '''on_update
        '''
        if flow.bidirectional_packets > self.n_packets:
            return
        
        if packet.protocol in [6, 17]:
            # nodes weights
            copied_binary_payload = []
            copied_binary_payload.extend(self.get_packet_as_binary_pypacker(packet))
            padding = self.MTU-len(copied_binary_payload)
            copied_binary_payload.extend(np.full(padding,0))
            flow.udps.simple_tgnn_nodes_weight_no_norm[flow.bidirectional_packets-1] = copied_binary_payload
            copied_binary_payload = [float(i)/255 for i in copied_binary_payload]
            # copied_binary_payload.extend(np.full(padding,0))
            flow.udps.simple_tgnn_nodes_weight[flow.bidirectional_packets-1] = copied_binary_payload

            # Nodes timestamps for Edge inter-arrival time weights
            packet_timestamp = packet.time
            flow.udps.simple_tgnn_timestamp[flow.bidirectional_packets-1] = packet_timestamp
            
            # Graph meta atttributes
            payload_length = packet.payload_size
            packet_length = packet.ip_size

            flow.udps.simple_tgnn_payload_length.push(payload_length)
            flow.udps.simple_tgnn_packet_length.push(packet_length)




        
        
    def on_expire(self, flow):
        '''on_expire
        '''
        flow.udps.simple_tgnn_graph_meta_attr = [flow.udps.simple_tgnn_payload_length.mean(),
                           flow.udps.simple_tgnn_payload_length.stddev() if flow.udps.simple_tgnn_payload_length._count >= 2 else 0,
                           flow.udps.simple_tgnn_packet_length.mean(),
                           flow.udps.simple_tgnn_packet_length.stddev() if flow.udps.simple_tgnn_packet_length._count >= 2 else 0,
                           flow.bidirectional_duration_ms/1000]
        flow.udps.simple_tgnn_graph_meta_attr_no_norm = flow.udps.simple_tgnn_graph_meta_attr
        flow.udps.simple_tgnn_graph_meta_attr = [float(i)/max(flow.udps.simple_tgnn_graph_meta_attr) for i in flow.udps.simple_tgnn_graph_meta_attr]
        flow.udps.simple_tgnn_timestamp[flow.udps.simple_tgnn_timestamp == 0] = flow.udps.simple_tgnn_timestamp.max()
        graph = generate_simple_GNN(self.n_packets,flow.udps.simple_tgnn_timestamp)
        flow.udps.simple_tgnn_edges_weight = graph.edges_weight.tolist()
        flow.udps.simple_tgnn_sender_vector = graph.sender_vector.tolist()
        flow.udps.simple_tgnn_receiver_vector = graph.receiver_vector.tolist()
        flow.udps.simple_tgnn_timestamp = flow.udps.simple_tgnn_timestamp.tolist()
        flow.udps.simple_tgnn_nodes_weight = flow.udps.simple_tgnn_nodes_weight.tolist()
        del flow.udps.simple_tgnn_payload_length
        del flow.udps.simple_tgnn_packet_length
    
    def get_packet_as_binary_pypacker(self, packet):
        '''
        Scapy has a bug with correctly dissecting SNMP payload.
        '''
        return raw(packet.ip_packet)
    
    def get_payload_as_binary(self, packet):
        return packet.ip_packet[-packet.payload_size:]
    
    def get_payload_as_binary_scapy(self, packet):
        '''
        Older versions of NFStream (lower than 6.1) has problems with 
        detection the correct payload size of ipv6 packets.
        This function is here as a fallback in case of problems in future
        versions.

        in 6.4.2 and 6.4.3 there is a bug with wrong transport_size, also
        NFStream does not detect ethernet padding.
        '''
        ip_version = packet.ip_version
        if ip_version == 4:
            scapy_packet = IP(packet.ip_packet)
        elif ip_version == 6:
            scapy_packet = IPv6(packet.ip_packet)

        return raw(scapy_packet.payload.payload)
    
    @staticmethod
    def preprocess(dataframe):
        ''' 
        Preprocessing method for the GraphDApp features.
        Converting 'udps.simple_tig_adj' and 'udps.simple_tig_features' columns from str to 2D-list.
        '''
        import ast
        # validate
        assert 'udps.simple_tgnn_nodes_weight' in dataframe.columns, "Column 'udps.simple_tgnn_nodes_weight' not found."
        assert isinstance(dataframe['udps.simple_tgnn_nodes_weight'].iloc[0], str), "Values in column 'udps.simple_tgnn_nodes_weight' are already processed."

        dataframe['udps.simple_tgnn_nodes_weight'] = dataframe['udps.simple_tgnn_nodes_weight'].apply(ast.literal_eval)

        assert 'udps.simple_tgnn_edges_weight' in dataframe.columns, "Column 'udps.simple_tgnn_edges_weight' not found."
        assert isinstance(dataframe['udps.simple_tgnn_edges_weight'].iloc[0], str), "Values in column 'udps.simple_tgnn_edges_weight' are already processed."
        
        dataframe['udps.simple_tgnn_edges_weight'] = dataframe['udps.simple_tgnn_edges_weight'].apply(ast.literal_eval)



def generate_simple_GNN(nodes,nodes_connection_values):
    graph = Graph(nodes, nodes_connection_values)
    graph.chronologic_relationship()
    return graph


class Graph:
    def __init__(self, n, timestamps):
        self.n = n
        self.timestamps = timestamps
        self.edge_num = int((self.n*(self.n-1))/2)
        self.sender_vector = np.zeros((self.edge_num))
        self.receiver_vector = np.zeros((self.edge_num))
        self.edges_weight = np.zeros((self.edge_num,1))
    
    def connect(self, v1, v2, edge_num):
        self.sender_vector[edge_num] = v1
        self.receiver_vector[edge_num] = v2
        self.edges_weight[edge_num] = self.timestamps[v2] - self.timestamps[v1]
    
    def chronologic_relationship(self):
        for i in range(0,self.n-1):
            self.edges_weight[i] = self.timestamps[i+1]-self.timestamps[i]
            self.sender_vector[i] = i
            self.receiver_vector[i] = i + 1

        count = self.n-1
        for i in range(0,self.n):
            for num,j in enumerate(range(i+2,self.n)):
                self.connect(i,j,count+num)
            count = count + num + 1
