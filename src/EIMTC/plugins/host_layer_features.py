from nfstream import NFPlugin
from hashlib import md5
from main import some_val

class HostLayerFeatures(NFPlugin):
    '''
        EXPERIMENTAL
    
    '''
    def __init__(self, **kwargs): 
        super().__init__(**kwargs)
        self.hosts = dict()

    def on_init(self, packet, flow):
        id = self._five_tuple_string_of(flow)
        if flow.src_ip not in self.hosts:
            self.hosts[flow.src_ip] = Host(flow.src_ip)
        if flow.dst_ip not in self.hosts:
            self.hosts[flow.dst_ip] = Host(flow.dst_ip)
        

    def on_update(self, packet, flow):
        src_host = self.hosts[packet.src_ip]
        src_host.sent_packets += 1
        
        global some_val
        some_val += 1
        
        

    def _five_tuple_string_of(self, obj):
        return md5(
            str.join('',
                sorted([
                    obj.src_ip,
                    str(obj.src_port),
                    obj.dst_ip,
                    str(obj.dst_port),
                    str(obj.protocol)])))

        
        
        
class Host:
    def __init__(self, ip: str) -> None:
        self.ip = ip
        # default values
        self.recv_packets = 0
        self.recv_bytes   = 0
        self.sent_packets = 0
        self.sent_bytes   = 0
    
    
    def __hash__(self) -> int:
        pass

    def __str__(self) -> str:
        '''
        for debug purposes.
        '''
        
        pass