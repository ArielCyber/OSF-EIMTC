from nfstream import NFPlugin
from scapy.all import IP, DNS, IPv6
from ..stats.stats import IterableStats

class DNSCounter(NFPlugin):
    '''
    Description:
        DNS over UDP only, supports MDNS (Multicast DNS)
        
    Features (bidirectional and unidirectional per direction):
        dns_packets   
        dns_queries   
        dns_responses 
        dns_qd_count  
        dns_an_count
        dns_ns_count
        dns_ar_count
        dns_response_digit_count (+ mean)
        dns_response_alpha_count (+ mean)
        dns_response_hypens_count (+ mean)
        dns_response_dots_count (+ mean)
        dns_response_ip_count (+ mean)
        dns_response_ttls_s (seconds) (+ Stats)
        
    Prefixes:
        bidirectional_
        src2dst_
        dst2src_
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_init(self, packet, flow):
        '''
        on_init(self, packet, flow): Method called at flow creation.
        '''
        # bidirectional
        flow.udps.bidirectional_dns_packets   = 0
        flow.udps.bidirectional_dns_queries   = 0
        flow.udps.bidirectional_dns_responses = 0
        flow.udps.bidirectional_dns_qd_count  = 0
        flow.udps.bidirectional_dns_an_count  = 0 # answer count
        flow.udps.bidirectional_dns_ns_count  = 0 # name server count
        flow.udps.bidirectional_dns_ar_count  = 0 # additional information count
        flow.udps.bidirectional_dns_response_digit_count  = 0 # count of digits in DNS response.
        flow.udps.bidirectional_dns_response_alpha_count  = 0 # count of alpha in DNS response.
        flow.udps.bidirectional_dns_response_hypens_count = 0 # count of hypens in DNS response.
        flow.udps.bidirectional_dns_response_dots_count   = 0 # count of dots in DNS response.
        flow.udps.bidirectional_dns_response_ip_count     = 0 # number ips in response.
        flow.udps.bidirectional_dns_response_ttls_s       = [] # record Time-To-Live values in seconds.
        flow.udps.bidirectional_mean_dns_response_digit_count  = 0 # mean relative to total number of responses
        flow.udps.bidirectional_mean_dns_response_alpha_count  = 0 
        flow.udps.bidirectional_mean_dns_response_hypens_count = 0 
        flow.udps.bidirectional_mean_dns_response_dots_count   = 0 
        flow.udps.bidirectional_mean_dns_response_ip_count     = 0 
        flow.udps.bidirectional_mean_dns_response_ttls_s             = None
        flow.udps.bidirectional_median_dns_response_ttls_s           = None
        flow.udps.bidirectional_stdev_dns_response_ttls_s            = None
        flow.udps.bidirectional_variance_dns_response_ttls_s         = None
        flow.udps.bidirectional_coeff_of_var_dns_response_ttls_s     = None
        flow.udps.bidirectional_skew_from_median_dns_response_ttls_s = None
        flow.udps.bidirectional_min_dns_response_ttls_s              = None
        flow.udps.bidirectional_max_dns_response_ttls_s              = None
        # src -> dst
        flow.udps.src2dst_dns_packets   = 0
        flow.udps.src2dst_dns_queries   = 0
        flow.udps.src2dst_dns_responses = 0
        flow.udps.src2dst_dns_qd_count  = 0
        flow.udps.src2dst_dns_an_count  = 0 # answer count
        flow.udps.src2dst_dns_ns_count  = 0 # name server count
        flow.udps.src2dst_dns_ar_count  = 0 # additional information count
        flow.udps.src2dst_dns_response_digit_count  = 0 # count of digits in DNS response.
        flow.udps.src2dst_dns_response_alpha_count  = 0 # count of alpha in DNS response.
        flow.udps.src2dst_dns_response_hypens_count = 0 # count of hypens in DNS response.
        flow.udps.src2dst_dns_response_dots_count   = 0 # count of dots in DNS response.
        flow.udps.src2dst_dns_response_ip_count     = 0 # number ips in response.
        flow.udps.src2dst_dns_response_ttls_s       = [] # record Time-To-Live values in seconds.
        flow.udps.src2dst_dns_response_ttls_s       = [] # record Time-To-Live values in seconds.
        flow.udps.src2dst_mean_dns_response_digit_count  = 0 # mean relative to total number of responses
        flow.udps.src2dst_mean_dns_response_alpha_count  = 0 
        flow.udps.src2dst_mean_dns_response_hypens_count = 0 
        flow.udps.src2dst_mean_dns_response_dots_count   = 0 
        flow.udps.src2dst_mean_dns_response_ip_count     = 0 
        flow.udps.src2dst_mean_dns_response_ttls_s             = None
        flow.udps.src2dst_median_dns_response_ttls_s           = None
        flow.udps.src2dst_stdev_dns_response_ttls_s            = None
        flow.udps.src2dst_variance_dns_response_ttls_s         = None
        flow.udps.src2dst_coeff_of_var_dns_response_ttls_s     = None
        flow.udps.src2dst_skew_from_median_dns_response_ttls_s = None
        flow.udps.src2dst_min_dns_response_ttls_s              = None
        flow.udps.src2dst_max_dns_response_ttls_s              = None
        # dst -> src
        flow.udps.dst2src_dns_packets   = 0
        flow.udps.dst2src_dns_queries   = 0
        flow.udps.dst2src_dns_responses = 0
        flow.udps.dst2src_dns_qd_count  = 0
        flow.udps.dst2src_dns_an_count  = 0 # answer count
        flow.udps.dst2src_dns_ns_count  = 0 # name server count
        flow.udps.dst2src_dns_ar_count  = 0 # additional information count
        flow.udps.dst2src_dns_response_digit_count  = 0 # count of digits in DNS response.
        flow.udps.dst2src_dns_response_alpha_count  = 0 # count of alpha in DNS response.
        flow.udps.dst2src_dns_response_hypens_count = 0 # count of hypens in DNS response.
        flow.udps.dst2src_dns_response_dots_count   = 0 # count of dots in DNS response.
        flow.udps.dst2src_dns_response_ip_count     = 0 # number ips in response.
        flow.udps.dst2src_dns_response_ttls_s       = [] # record Time-To-Live values in seconds.
        flow.udps.dst2src_mean_dns_response_digit_count  = 0 # mean relative to total number of responses
        flow.udps.dst2src_mean_dns_response_alpha_count  = 0 
        flow.udps.dst2src_mean_dns_response_hypens_count = 0 
        flow.udps.dst2src_mean_dns_response_dots_count   = 0 
        flow.udps.dst2src_mean_dns_response_ip_count     = 0 
        flow.udps.dst2src_mean_dns_response_ttls_s             = None
        flow.udps.dst2src_median_dns_response_ttls_s           = None
        flow.udps.dst2src_stdev_dns_response_ttls_s            = None
        flow.udps.dst2src_variance_dns_response_ttls_s         = None
        flow.udps.dst2src_coeff_of_var_dns_response_ttls_s     = None
        flow.udps.dst2src_skew_from_median_dns_response_ttls_s = None
        flow.udps.dst2src_min_dns_response_ttls_s              = None
        flow.udps.dst2src_max_dns_response_ttls_s              = None
                
        self.on_update(packet, flow)

    def on_update(self, packet, flow):
        if flow.protocol == 17: # 17=UDP, 6=TCP
            ip_packet = IP(packet.ip_packet)
            if ip_packet[IP].version == 6:
                ip_packet = IPv6(packet.ip_packet)
            if DNS in ip_packet:
                dns_packet = ip_packet[DNS]
                if packet.direction == 0: # src2dst
                    flow.udps.src2dst_dns_packets  += 1
                    flow.udps.src2dst_dns_qd_count += dns_packet.qdcount
                    flow.udps.src2dst_dns_an_count += dns_packet.ancount
                    flow.udps.src2dst_dns_ns_count += dns_packet.nscount
                    flow.udps.src2dst_dns_ar_count += dns_packet.arcount
                    if dns_packet.qr == 0: # DNS query
                        flow.udps.src2dst_dns_queries += 1
                    elif dns_packet.qr == 1: # DNS response
                        flow.udps.src2dst_dns_responses += 1
                        flow.udps.src2dst_dns_response_digit_count  = self._count_rrname_char_of(dns_packet, lambda c: c.isdigit()) # counting digits 
                        flow.udps.src2dst_dns_response_alpha_count  = self._count_rrname_char_of(dns_packet, lambda c: c.isalpha()) # counting letters
                        flow.udps.src2dst_dns_response_hypens_count = self._count_rrname_char_of(dns_packet, lambda c: c == '-') # counting hypens
                        flow.udps.src2dst_dns_response_dots_count   = self._count_rrname_char_of(dns_packet, lambda c: c == '.') # counting dots
                        flow.udps.src2dst_dns_response_ip_count     = self._count_number_of_ip(dns_packet)
                        flow.udps.src2dst_dns_response_ttls_s.extend(self._ttl_values(dns_packet))
                        
                else: # dst2src
                    flow.udps.dst2src_dns_packets  += 1
                    flow.udps.dst2src_dns_qd_count += dns_packet.qdcount
                    flow.udps.dst2src_dns_an_count += dns_packet.ancount
                    flow.udps.dst2src_dns_ns_count += dns_packet.nscount
                    flow.udps.dst2src_dns_ar_count += dns_packet.arcount
                    if dns_packet.qr == 0: # DNS query
                        flow.udps.dst2src_dns_queries += 1
                    elif dns_packet.qr == 1: # DNS response
                        flow.udps.dst2src_dns_responses += 1
                        flow.udps.dst2src_dns_response_digit_count  = self._count_rrname_char_of(dns_packet, lambda c: c.isdigit()) # counting digits 
                        flow.udps.dst2src_dns_response_alpha_count  = self._count_rrname_char_of(dns_packet, lambda c: c.isalpha()) # counting letters
                        flow.udps.dst2src_dns_response_hypens_count = self._count_rrname_char_of(dns_packet, lambda c: c == '-') # counting hypens
                        flow.udps.dst2src_dns_response_dots_count   = self._count_rrname_char_of(dns_packet, lambda c: c == '.') # counting dots
                        flow.udps.dst2src_dns_response_ip_count     = self._count_number_of_ip(dns_packet)
                        flow.udps.dst2src_dns_response_ttls_s.extend(self._ttl_values(dns_packet))
                        
                # compute/update bidirectional by merging both directions.
                flow.udps.bidirectional_dns_packets   = flow.udps.src2dst_dns_packets   + flow.udps.dst2src_dns_packets
                flow.udps.bidirectional_dns_queries   = flow.udps.src2dst_dns_queries   + flow.udps.dst2src_dns_queries
                flow.udps.bidirectional_dns_responses = flow.udps.src2dst_dns_responses + flow.udps.dst2src_dns_responses 
                flow.udps.bidirectional_dns_qd_count  = flow.udps.src2dst_dns_qd_count  + flow.udps.dst2src_dns_qd_count
                flow.udps.bidirectional_dns_an_count  = flow.udps.src2dst_dns_an_count  + flow.udps.dst2src_dns_an_count
                flow.udps.bidirectional_dns_ns_count  = flow.udps.src2dst_dns_ns_count  + flow.udps.dst2src_dns_ns_count
                flow.udps.bidirectional_dns_ar_count  = flow.udps.src2dst_dns_ar_count  + flow.udps.dst2src_dns_ar_count
                flow.udps.bidirectional_dns_response_digit_count  = flow.udps.src2dst_dns_response_digit_count  + flow.udps.dst2src_dns_response_digit_count
                flow.udps.bidirectional_dns_response_alpha_count  = flow.udps.src2dst_dns_response_alpha_count  + flow.udps.dst2src_dns_response_alpha_count
                flow.udps.bidirectional_dns_response_hypens_count = flow.udps.src2dst_dns_response_hypens_count + flow.udps.dst2src_dns_response_hypens_count
                flow.udps.bidirectional_dns_response_dots_count   = flow.udps.src2dst_dns_response_dots_count   + flow.udps.dst2src_dns_response_dots_count
                flow.udps.bidirectional_dns_response_ip_count     = flow.udps.src2dst_dns_response_ip_count     + flow.udps.dst2src_dns_response_ip_count 
                flow.udps.bidirectional_dns_response_ttls_s       = flow.udps.src2dst_dns_response_ttls_s       + flow.udps.dst2src_dns_response_ttls_s
    
    def on_expire(self, flow):
        # TTLS
        # src -> dst
        if len(flow.udps.src2dst_dns_response_ttls_s) > 0:
            src2dst_stats = IterableStats(flow.udps.src2dst_dns_response_ttls_s)
            flow.udps.src2dst_mean_dns_response_ttls_s         = src2dst_stats.average()
            flow.udps.src2dst_median_dns_response_ttls_s       = src2dst_stats.median()
            flow.udps.src2dst_stdev_dns_response_ttls_s        = src2dst_stats.std_deviation()
            flow.udps.src2dst_variance_dns_response_ttls_s     = src2dst_stats.variance()
            flow.udps.src2dst_coeff_of_var_dns_response_ttls_s = src2dst_stats.coeff_of_variation()
            flow.udps.src2dst_skew_from_median_dns_response_ttls_s = src2dst_stats.skew_from_median()
            flow.udps.src2dst_min_dns_response_ttls_s          = src2dst_stats.min()
            flow.udps.src2dst_max_dns_response_ttls_s          = src2dst_stats.max()
        else: 
            flow.udps.src2dst_dns_response_ttls_s = None
        # dst -> src
        if len(flow.udps.dst2src_dns_response_ttls_s) > 0:
            dst2src_stats = IterableStats(flow.udps.dst2src_dns_response_ttls_s)
            flow.udps.dst2src_mean_dns_response_ttls_s             = dst2src_stats.average()
            flow.udps.dst2src_median_dns_response_ttls_s           = dst2src_stats.median()
            flow.udps.dst2src_stdev_dns_response_ttls_s            = dst2src_stats.std_deviation()
            flow.udps.dst2src_variance_dns_response_ttls_s         = dst2src_stats.variance()
            flow.udps.dst2src_coeff_of_var_dns_response_ttls_s     = dst2src_stats.coeff_of_variation()
            flow.udps.dst2src_skew_from_median_dns_response_ttls_s = dst2src_stats.skew_from_median()
            flow.udps.dst2src_min_dns_response_ttls_s              = dst2src_stats.min()
            flow.udps.dst2src_max_dns_response_ttls_s              = dst2src_stats.max()
        else: 
            flow.udps.dst2src_dns_response_ttls_s = None
        # bidirectional
        if len(flow.udps.bidirectional_dns_response_ttls_s) > 0:
            bi_stats = IterableStats(flow.udps.bidirectional_dns_response_ttls_s)
            flow.udps.bidirectional_mean_dns_response_ttls_s             = bi_stats.average()
            flow.udps.bidirectional_median_dns_response_ttls_s           = bi_stats.median()
            flow.udps.bidirectional_stdev_dns_response_ttls_s            = bi_stats.std_deviation()
            flow.udps.bidirectional_variance_dns_response_ttls_s         = bi_stats.variance()
            flow.udps.bidirectional_coeff_of_var_dns_response_ttls_s     = bi_stats.coeff_of_variation()
            flow.udps.bidirectional_skew_from_median_dns_response_ttls_s = bi_stats.skew_from_median()
            flow.udps.bidirectional_min_dns_response_ttls_s              = bi_stats.min()
            flow.udps.bidirectional_max_dns_response_ttls_s              = bi_stats.max()
        else: 
            flow.udps.bidirectional_dns_response_ttls_s = None
            
        # Char/Digits/Dots/Hypens
        # src -> dst
        if flow.udps.src2dst_dns_responses > 0:
            flow.udps.src2dst_mean_dns_response_digit_count  = flow.udps.src2dst_dns_response_digit_count  / flow.udps.src2dst_dns_responses
            flow.udps.src2dst_mean_dns_response_alpha_count  = flow.udps.src2dst_dns_response_alpha_count  / flow.udps.src2dst_dns_responses
            flow.udps.src2dst_mean_dns_response_dots_count   = flow.udps.src2dst_dns_response_dots_count   / flow.udps.src2dst_dns_responses
            flow.udps.src2dst_mean_dns_response_ip_count     = flow.udps.src2dst_dns_response_ip_count     / flow.udps.src2dst_dns_responses
            flow.udps.src2dst_mean_dns_response_hypens_count = flow.udps.src2dst_dns_response_hypens_count / flow.udps.src2dst_dns_responses
        # dst -> src
        if flow.udps.dst2src_dns_responses > 0:
            flow.udps.dst2src_mean_dns_response_digit_count  = flow.udps.dst2src_dns_response_digit_count  / flow.udps.dst2src_dns_responses
            flow.udps.dst2src_mean_dns_response_alpha_count  = flow.udps.dst2src_dns_response_alpha_count  / flow.udps.dst2src_dns_responses
            flow.udps.dst2src_mean_dns_response_dots_count   = flow.udps.dst2src_dns_response_dots_count   / flow.udps.dst2src_dns_responses
            flow.udps.dst2src_mean_dns_response_ip_count     = flow.udps.dst2src_dns_response_ip_count     / flow.udps.dst2src_dns_responses
            flow.udps.dst2src_mean_dns_response_hypens_count = flow.udps.dst2src_dns_response_hypens_count / flow.udps.dst2src_dns_responses
        # bidir
        if flow.udps.bidirectional_dns_responses > 0:
            flow.udps.bidirectional_mean_dns_response_digit_count  = flow.udps.bidirectional_dns_response_digit_count  / flow.udps.bidirectional_dns_responses
            flow.udps.bidirectional_mean_dns_response_alpha_count  = flow.udps.bidirectional_dns_response_alpha_count  / flow.udps.bidirectional_dns_responses
            flow.udps.bidirectional_mean_dns_response_dots_count   = flow.udps.bidirectional_dns_response_dots_count   / flow.udps.bidirectional_dns_responses
            flow.udps.bidirectional_mean_dns_response_ip_count     = flow.udps.bidirectional_dns_response_ip_count     / flow.udps.bidirectional_dns_responses
            flow.udps.bidirectional_mean_dns_response_hypens_count = flow.udps.bidirectional_dns_response_hypens_count / flow.udps.bidirectional_dns_responses
    
    def _count_rrname_char_of(self, dns_res_packet, count_func):
        resource_record_names = []
        for i in range(dns_res_packet.ancount):
            dns_ans_record = dns_res_packet.an[i]
            resource_record_names += str(dns_ans_record.rrname)[2:-2]
        total_digit_count  = sum(count_func(c) for c in resource_record_names)
        
        return total_digit_count
    
    def _count_number_of_ip(self, dns_res_packet):
        # Note: not tested
        '''
            Records: 
                A=1 (0x01)
                AAAA=28 (0x1c)
        '''
        ip_count = 0
        for i in range(dns_res_packet.ancount):
            dns_ans_record = dns_res_packet.an[i]
            if dns_ans_record.type in [1, 28]:
                ip_count += 1
                
        return ip_count
        
    def _ttl_values(self, dns_res_packet):
        ttls = []
        for i in range(dns_res_packet.ancount):
            dns_ans_record = dns_res_packet.an[i]
            ttls.append(dns_ans_record.ttl)
                
        return ttls
    
            
            
            

