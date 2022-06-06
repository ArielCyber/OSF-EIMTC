from nfstream import NFPlugin
import pyasn
import functools
import pandas as pd
from os import path

class ASNInfo(NFPlugin):
    '''
    Description:
        Extracts ASN related info from source and destination ip addresses.
        By using databases along with 'pyasn' Python module.
        DB required: 
            1. pyasn.db or equavalent, please see 'IPASN Data Files' section in: 
            https://github.com/hadiasghari/pyasn to aquire it.
            2. TSV (tab separated values) DB file of contextual info such as from https://iptoasn.com
            
    Features:
        asn_number
        asn_country_code
        asn_description
        
    Feature prefixes:
        src_
        dst_
    '''
    def __init__(self, pyasn_context_file=path.join(path.dirname(__file__), '../tools/pyasn.db'), 
                as_contextual_file=path.join(path.dirname(__file__),'../tools/ip2asn-v4.tsv'), **kwargs):
        super().__init__(**kwargs)
        self.pyasn_contextual_data = pyasn.pyasn(pyasn_context_file)
        self.as_contextual_data = pd.read_csv(as_contextual_file, 
                                            sep='\t', 
                                            names=[
                                                'range_start',
                                                'range_end', 
                                                'AS_number', 
                                                'country_code', 
                                                'AS_description'
                                            ])

    def on_init(self, packet, flow):
        flow.udps.src_asn_number       = None
        flow.udps.src_asn_country_code = None
        flow.udps.src_asn_description  = None
        flow.udps.dst_asn_number       = None
        flow.udps.dst_asn_country_code = None
        flow.udps.dst_asn_description  = None
        # src asn info
        src_asn_info = self.get_asn_info(flow.src_ip)
        if src_asn_info is not None:
            flow.udps.src_asn_number       = src_asn_info['AS_number']
            flow.udps.src_asn_country_code = src_asn_info['country_code']
            flow.udps.src_asn_description  = src_asn_info['AS_description']
        # dst asn info
        dst_asn_info = self.get_asn_info(flow.dst_ip)
        if dst_asn_info is not None:
            flow.udps.dst_asn_number       = dst_asn_info['AS_number']
            flow.udps.dst_asn_country_code = dst_asn_info['country_code']
            flow.udps.dst_asn_description  = dst_asn_info['AS_description']

    # extracted with modification from https://github.com/cisco/mercury/blob/c8ad79d56959ba1092e686b23c1b6f60961600c7/src/python-inference/tls_fingerprint_min.pyx
    MAX_CACHED_RESULTS = 2**16
    @functools.lru_cache(maxsize=MAX_CACHED_RESULTS)
    def get_asn_info(self, ip_addr: str):
        try:
            asn_n,_ = self.pyasn_contextual_data.lookup(ip_addr)
            if asn_n != None:
                return self.as_contextual_data[self.as_contextual_data['AS_number'] == asn_n].iloc[0]
        except:
            pass

        return None