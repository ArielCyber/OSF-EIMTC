# used for byte frequency analysis

from nfstream import NFPlugin
import numpy as np # for bytes distribution

class ByteFrequency(NFPlugin):
    '''
        NOTE: DEPRECTATED IN FAVOR OF NPacketsByteFrequency,
        has the same behavior as NPacketsByteFrequency(n_first_packets=0)
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_init(self, packet, flow):
        '''
        on_init(self, packet, flow): Method called at flow creation.
        '''

        flow.udps.bytes_frequency = np.zeros(256) # of ip payload onwards
        
        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        self._add_payload_bytes_frequency(packet.ip_packet, flow.udps.bytes_frequency)

    def on_expire(self, flow):
        pass

    def _add_payload_bytes_frequency(self, payload, container):
        payload_bytes_array = np.frombuffer(payload, dtype='B') # 'B' unsigned byte
        container[payload_bytes_array] += 1