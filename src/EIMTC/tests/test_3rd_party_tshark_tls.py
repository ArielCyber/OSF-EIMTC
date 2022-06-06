import unittest
from os import path
import pandas as pd
import numpy as np
from numpy.testing import assert_array_equal
from EIMTC.tls_tshark_entry import _extract_tls_features, _read_config_file

dirname = path.dirname(__file__)
pcaps_dir = path.join(dirname, 'pcaps')


class Test3rdPartyTSharkForTLS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = _read_config_file(
            path.join(path.dirname(__file__), '../tools/config.json')
        )
        
    def test_tls_client_hello_single_packet(self):
        # Given
        pcap_filepath = path.join(pcaps_dir, 'tls_client_hello_single_packet.pcap')
        # When
        df: pd.DataFrame = _extract_tls_features(pcap_filepath, self.config['tshark_location'])
        # Then
        self.assertFalse(df.empty) 
        ## Stats
        ## Stats | Bidirectional
        assert_array_equal(df['bidirectional_tls_records'], [1])
        assert_array_equal(df['bidirectional_tls_payload_bytes'], [512])
        assert_array_equal(df['bidirectional_tls_record_distinct_sizes'], [1])
        assert_array_equal(df['bidirectional_mean_tls_record_size'], [512])
        assert_array_equal(df['bidirectional_median_tls_record_size'], [512])
        assert_array_equal(df['bidirectional_stddev_tls_record_size'], [np.nan])
        assert_array_equal(df['bidirectional_variance_tls_record_size'], [np.nan])
        assert_array_equal(df['bidirectional_skew_from_median_tls_record_size'], [np.nan])
        assert_array_equal(df['bidirectional_coeff_of_var_tls_record_size'], [np.nan])
        assert_array_equal(df['bidirectional_min_tls_record_size'], [512])
        assert_array_equal(df['bidirectional_max_tls_record_size'], [512])
        ## Stats | src -> dst
        assert_array_equal(df['src2dst_tls_records'], [1])
        assert_array_equal(df['src2dst_tls_payload_bytes'], [512])
        assert_array_equal(df['src2dst_tls_record_distinct_sizes'], [1])
        assert_array_equal(df['src2dst_mean_tls_record_size'], [512])
        assert_array_equal(df['src2dst_median_tls_record_size'], [512])
        assert_array_equal(df['src2dst_stddev_tls_record_size'], [np.nan])
        assert_array_equal(df['src2dst_variance_tls_record_size'], [np.nan])
        assert_array_equal(df['src2dst_skew_from_median_tls_record_size'], [np.nan])
        assert_array_equal(df['src2dst_coeff_of_var_tls_record_size'], [np.nan])
        assert_array_equal(df['src2dst_min_tls_record_size'], [512])
        assert_array_equal(df['src2dst_max_tls_record_size'], [512])
        ## Stats | dst -> src
        assert_array_equal(df['dst2src_tls_records'], [0])
        assert_array_equal(df['dst2src_tls_payload_bytes'], [0])
        assert_array_equal(df['dst2src_tls_record_distinct_sizes'], [0])
        assert_array_equal(df['dst2src_mean_tls_record_size'], [np.nan])
        assert_array_equal(df['dst2src_median_tls_record_size'], [np.nan])
        assert_array_equal(df['dst2src_stddev_tls_record_size'], [np.nan])
        assert_array_equal(df['dst2src_variance_tls_record_size'], [np.nan])
        assert_array_equal(df['dst2src_skew_from_median_tls_record_size'], [np.nan])
        assert_array_equal(df['dst2src_coeff_of_var_tls_record_size'], [np.nan])
        assert_array_equal(df['dst2src_min_tls_record_size'], [np.nan])
        assert_array_equal(df['dst2src_max_tls_record_size'], [np.nan])
        ## Clumps
        ## Clumps | Bidirectional
        assert_array_equal(df['bidirectional_tls_clumps'], [1])
        assert_array_equal(df['bidirectional_mean_tls_clump_bytes'], [512])
        assert_array_equal(df['bidirectional_median_tls_clump_bytes'], [512])
        assert_array_equal(df['bidirectional_stddev_tls_clump_bytes'], [np.nan])
        assert_array_equal(df['bidirectional_variance_tls_clump_bytes'], [np.nan])
        assert_array_equal(df['bidirectional_skew_from_median_tls_clump_bytes'], [np.nan])
        assert_array_equal(df['bidirectional_coeff_of_var_tls_clump_bytes'], [np.nan])
        assert_array_equal(df['bidirectional_min_tls_clump_bytes'], [512])
        assert_array_equal(df['bidirectional_max_tls_clump_bytes'], [512])
        assert_array_equal(df['bidirectional_mean_tls_clump_sizes'], [1])
        assert_array_equal(df['bidirectional_median_tls_clump_sizes'], [1])
        assert_array_equal(df['bidirectional_stddev_tls_clump_sizes'], [np.nan])
        assert_array_equal(df['bidirectional_variance_tls_clump_sizes'], [np.nan])
        assert_array_equal(df['bidirectional_skew_from_median_tls_clump_sizes'], [np.nan])
        assert_array_equal(df['bidirectional_coeff_of_var_tls_clump_sizes'], [np.nan])
        assert_array_equal(df['bidirectional_min_tls_clump_sizes'], [1])
        assert_array_equal(df['bidirectional_max_tls_clump_sizes'], [1])
        ## Clumps | src -> dst
        assert_array_equal(df['src2dst_tls_clumps'], [1])
        assert_array_equal(df['src2dst_mean_tls_clump_bytes'], [512])
        assert_array_equal(df['src2dst_median_tls_clump_bytes'], [512])
        assert_array_equal(df['src2dst_stddev_tls_clump_bytes'], [np.nan])
        assert_array_equal(df['src2dst_variance_tls_clump_bytes'], [np.nan])
        assert_array_equal(df['src2dst_skew_from_median_tls_clump_bytes'], [np.nan])
        assert_array_equal(df['src2dst_coeff_of_var_tls_clump_bytes'], [np.nan])
        assert_array_equal(df['src2dst_min_tls_clump_bytes'], [512])
        assert_array_equal(df['src2dst_max_tls_clump_bytes'], [512])
        assert_array_equal(df['src2dst_mean_tls_clump_sizes'], [1])
        assert_array_equal(df['src2dst_median_tls_clump_sizes'], [1])
        assert_array_equal(df['src2dst_stddev_tls_clump_sizes'], [np.nan])
        assert_array_equal(df['src2dst_variance_tls_clump_sizes'], [np.nan])
        assert_array_equal(df['src2dst_skew_from_median_tls_clump_sizes'], [np.nan])
        assert_array_equal(df['src2dst_coeff_of_var_tls_clump_sizes'], [np.nan])
        assert_array_equal(df['src2dst_min_tls_clump_sizes'], [1])
        assert_array_equal(df['src2dst_max_tls_clump_sizes'], [1])
        ## Clumps | dst -> src
        assert_array_equal(df['dst2src_tls_clumps'], [0])
        assert_array_equal(df['dst2src_mean_tls_clump_bytes'], [np.nan])
        assert_array_equal(df['dst2src_median_tls_clump_bytes'], [np.nan])
        assert_array_equal(df['dst2src_stddev_tls_clump_bytes'], [np.nan])
        assert_array_equal(df['dst2src_variance_tls_clump_bytes'], [np.nan])
        assert_array_equal(df['dst2src_skew_from_median_tls_clump_bytes'], [np.nan])
        assert_array_equal(df['dst2src_coeff_of_var_tls_clump_bytes'], [np.nan])
        assert_array_equal(df['dst2src_min_tls_clump_bytes'], [np.nan])
        assert_array_equal(df['dst2src_max_tls_clump_bytes'], [np.nan])
        assert_array_equal(df['dst2src_mean_tls_clump_sizes'], [np.nan])
        assert_array_equal(df['dst2src_median_tls_clump_sizes'], [np.nan])
        assert_array_equal(df['dst2src_stddev_tls_clump_sizes'], [np.nan])
        assert_array_equal(df['dst2src_variance_tls_clump_sizes'], [np.nan])
        assert_array_equal(df['dst2src_skew_from_median_tls_clump_sizes'], [np.nan])
        assert_array_equal(df['dst2src_coeff_of_var_tls_clump_sizes'], [np.nan])
        assert_array_equal(df['dst2src_min_tls_clump_sizes'], [np.nan])
        assert_array_equal(df['dst2src_max_tls_clump_sizes'], [np.nan])

    def test_tls_record_per_packet_single_session(self):
        # Given
        pcap_filepath = path.join(pcaps_dir, 'tls_pkt_rel_time_single.pcap')
        # When
        df: pd.DataFrame = _extract_tls_features(pcap_filepath, self.config['tshark_location'])
        # Then
        self.assertFalse(df.empty) 
        self.assertSequenceEqual(list(df['bidirectional_tls_records']), [8])
        self.assertSequenceEqual(list(df['bidirectional_tls_payload_bytes']), [836])
        self.assertSequenceEqual(list(df['bidirectional_tls_record_distinct_sizes']), [2])
        self.assertSequenceEqual(list(df['bidirectional_mean_tls_record_size']), [104.5])
        self.assertSequenceEqual(list(df['bidirectional_min_tls_record_size']), [39])
        self.assertSequenceEqual(list(df['bidirectional_max_tls_record_size']), [170])
    
    def test_tls_multirecord_in_packet_single_session(self):
        # Given
        pcap_filepath = path.join(pcaps_dir, 'tls_small_pkt_payload_ratio_single.pcap')
        # When
        df: pd.DataFrame = _extract_tls_features(pcap_filepath, self.config['tshark_location'])
        # Then
        self.assertFalse(df.empty) 
        self.assertSequenceEqual(list(df['bidirectional_tls_records']), [12])
        self.assertSequenceEqual(list(df['bidirectional_tls_payload_bytes']), [1809])
        self.assertSequenceEqual(list(df['bidirectional_tls_record_distinct_sizes']), [10])
        self.assertSequenceEqual(list(df['bidirectional_mean_tls_record_size']), [150.75])
        self.assertSequenceEqual(list(df['bidirectional_min_tls_record_size']), [1])
        self.assertSequenceEqual(list(df['bidirectional_max_tls_record_size']), [664])
