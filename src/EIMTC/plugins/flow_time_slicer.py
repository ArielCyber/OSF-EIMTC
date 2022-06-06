from nfstream import NFPlugin


class FlowTimeSlicer(NFPlugin):
    '''
        DOESNT WORK AS NFSTREAM DOESNT ALLOW TO EXPIRE
        A STREAM EXCLUDING THE CURRENT PACKET.
    '''
    def __init__(self, time: float, **kwargs):  # time in seconds
        super().__init__(**kwargs)
        self.time = time
        self.flow_last_slicing_times = dict()

    def on_init(self, packet, flow):
        flow_five_tuple_string = self._five_tuple_string_of(flow)
        if flow_five_tuple_string not in self.flow_last_slicing_times:
            self.flow_last_slicing_times[flow_five_tuple_string] = flow.bidirectional_first_seen_ms

    def on_update(self, packet, flow):
        flow_five_tuple_string = self._five_tuple_string_of(flow)
        flow_slice_start_time  = self.flow_last_slicing_times[flow_five_tuple_string]
        current_time = packet.time
        time_diff = current_time - flow_slice_start_time
        time_slice_ms = self.time * 1000

        if time_diff > time_slice_ms:
            flow.expiration_id = -1  # -1 value force expiration
            self.flow_last_slicing_times[flow_five_tuple_string] = current_time

    def _five_tuple_string_of(self, flow):
        return str.join('',
            sorted([
                flow.src_ip,
                str(flow.src_port),
                flow.dst_ip,
                str(flow.dst_port)]))
