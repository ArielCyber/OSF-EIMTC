from nfstream import NFPlugin
from scapy.all import IP, TLS, load_layer

load_layer("tls")
# requires scapy 2.4+

class TLSRecord(NFPlugin):
    '''
    WORK IN PROGRESS!!
        Extracts the following features:
        - Number of TLS packets.
        - Number of TLS records.
        - TLS record size.
        - TLS record type: change_cipher_spec(20), alert(21), handshake(22), application_data(23).
        - TLS record direction (src2dst = 0, dst2src = 1).

        Note that due to TCP segmentation, the plugin can sometimes
        not detect TLS records as they might be segmented across
        multiple packets, this plugin does not try to reassmble TCP stream
        in order to recover missing TLS records.
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_init(self, packet, flow):
        '''
        on_init(self, packet, flow): Method called at flow creation.
        '''

        flow.udps.src2dst_tls_packets = 0 # number of tls packets
        flow.udps.dst2src_tls_packets = 0
        flow.udps.bidirectional_tls_packets = 0
        flow.udps.src2dst_tls_records = 0
        flow.udps.dst2src_tls_records = 0
        flow.udps.bidirectional_tls_records = 0
        flow.udps.src2dst_tls_record_size_freq = list()
        flow.udps.dst2src_tls_record_size_freq = list()
        flow.udps.bidirectional_tls_record_size_freq = list()
        flow.udps.src2dst_tls_record_type_freq = {'handshake':0, 'application':0} # limited to only handshake and application types.
        flow.udps.dst2src_tls_record_type_freq = {'handshake':0, 'application':0}
        flow.udps.bidirectional_tls_record_type_freq = {'handshake':0, 'application':0} 

        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        ip_packet = IP(packet.ip_packet)
        if TLS in ip_packet:
            if packet.direction == 0: # src2dst
                flow.udps.src2dst_tls_packets += 1
                #self._increment_dict_value(flow.udps.src2dst_tls_record_type_freq, ?)

    def on_expire(self, flow):
        pass

    def _increment_dict_value(self, d :dict, key: int):
        if key not in d:
            d[key] = 0
        d[key] += 1

