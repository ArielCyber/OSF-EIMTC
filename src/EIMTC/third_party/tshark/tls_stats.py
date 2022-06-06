from .stats import IterableStats
import pandas as pd
import numpy as np


class TLSRecordStats:
    def __init__(self, bidir_lengths):
        bidir_lengths['tls.record.length'] = bidir_lengths['tls.record.length'].astype('uint16')
        self.bidir_lengths = bidir_lengths['tls.record.length']
        self.bidir_len_stats   = IterableStats(self.bidir_lengths)
        self.src2dst_lengths = bidir_lengths[bidir_lengths['direction'] == 0]['tls.record.length']
        self.src2dst_len_stats = IterableStats(self.src2dst_lengths)
        self.dst2src_lengths = bidir_lengths[bidir_lengths['direction'] == 1]['tls.record.length']
        self.dst2src_len_stats = IterableStats(self.dst2src_lengths)
    
    def length_stats(self):
        return pd.concat([
            self.bidirectional_length_stats(),
            self.src2dst_length_stats(),
            self.dst2src_length_stats()
        ])
    
    def bidirectional_length_stats(self):
        return pd.Series({
            'bidirectional_tls_records': len(self.bidir_lengths),
            'bidirectional_tls_payload_bytes': sum(self.bidir_lengths),
            'bidirectional_tls_record_distinct_sizes': len(np.unique(self.bidir_lengths)),
            'bidirectional_mean_tls_record_size':             self.bidir_len_stats.average(),
            'bidirectional_median_tls_record_size':           self.bidir_len_stats.median(),
            'bidirectional_stddev_tls_record_size':           self.bidir_len_stats.std_deviation(),
            'bidirectional_variance_tls_record_size':         self.bidir_len_stats.variance(),
            'bidirectional_skew_from_median_tls_record_size': self.bidir_len_stats.skew_from_median(),
            'bidirectional_coeff_of_var_tls_record_size':     self.bidir_len_stats.coeff_of_variation(),
            'bidirectional_min_tls_record_size':              self.bidir_len_stats.min(),
            'bidirectional_max_tls_record_size':              self.bidir_len_stats.max(),
        })
    
    def src2dst_length_stats(self):
        return pd.Series({
            'src2dst_tls_records': len(self.src2dst_lengths),
            'src2dst_tls_payload_bytes': sum(self.src2dst_lengths),
            'src2dst_tls_record_distinct_sizes': len(np.unique(self.src2dst_lengths)),
            'src2dst_mean_tls_record_size':             self.src2dst_len_stats.average(),
            'src2dst_median_tls_record_size':           self.src2dst_len_stats.median(),
            'src2dst_stddev_tls_record_size':           self.src2dst_len_stats.std_deviation(),
            'src2dst_variance_tls_record_size':         self.src2dst_len_stats.variance(),
            'src2dst_skew_from_median_tls_record_size': self.src2dst_len_stats.skew_from_median(),
            'src2dst_coeff_of_var_tls_record_size':     self.src2dst_len_stats.coeff_of_variation(),
            'src2dst_min_tls_record_size':              self.src2dst_len_stats.min(),
            'src2dst_max_tls_record_size':              self.src2dst_len_stats.max(),
        })
        
    def dst2src_length_stats(self):
        return pd.Series({
            'dst2src_tls_records': len(self.dst2src_lengths),
            'dst2src_tls_payload_bytes': sum(self.dst2src_lengths),
            'dst2src_tls_record_distinct_sizes': len(np.unique(self.dst2src_lengths)),
            'dst2src_mean_tls_record_size':             self.dst2src_len_stats.average(),
            'dst2src_median_tls_record_size':           self.dst2src_len_stats.median(),
            'dst2src_stddev_tls_record_size':           self.dst2src_len_stats.std_deviation(),
            'dst2src_variance_tls_record_size':         self.dst2src_len_stats.variance(),
            'dst2src_skew_from_median_tls_record_size': self.dst2src_len_stats.skew_from_median(),
            'dst2src_coeff_of_var_tls_record_size':     self.dst2src_len_stats.coeff_of_variation(),
            'dst2src_min_tls_record_size':              self.dst2src_len_stats.min(),
            'dst2src_max_tls_record_size':              self.dst2src_len_stats.max(),
        })
    
    @classmethod
    def available_feature_names(cls):
        return TLSRecordStats(
            pd.DataFrame({
                'tls.record.length': [],
                'direction': []
            })
        ).length_stats().index.to_list()
        
        
        
class TLSRecordClumpStats:
    def __init__(self, bidir_lengths):
        bidir_clumps = bidir_lengths.groupby('clump_num')
        self.bidir_lengths = bidir_clumps['tls.record.length'].sum()
        self.bytes_length_stats = IterableStats(self.bidir_lengths)
        self.sizes = bidir_clumps.size()
        self.sizes_stats = IterableStats(self.sizes)
        # src2dst
        src2dst_clumps = bidir_lengths[bidir_lengths['direction'] == 0].groupby('clump_num')
        self.src2dst_lengths = src2dst_clumps['tls.record.length'].sum()
        self.src2dst_bytes_length_stats = IterableStats(self.src2dst_lengths)
        self.src2dst_sizes = src2dst_clumps.size()
        self.src2dst_sizes_stats = IterableStats(self.src2dst_sizes)
        # dst2src
        dst2src_clumps = bidir_lengths[bidir_lengths['direction'] == 1].groupby('clump_num')
        self.dst2src_lengths = dst2src_clumps['tls.record.length'].sum()
        self.dst2src_bytes_length_stats = IterableStats(self.dst2src_lengths)
        self.dst2src_sizes = dst2src_clumps.size()
        self.dst2src_sizes_stats = IterableStats(self.dst2src_sizes)
        
    def clump_stats(self):
        return pd.concat([
            self.bidirectional_stats(),
            self.src2dst_stats(),
            self.dst2src_stats(),
        ])
        
    def bidirectional_stats(self):
        return pd.Series({
            'bidirectional_tls_clumps': len(self.bidir_lengths),
            'bidirectional_mean_tls_clump_bytes':             self.bytes_length_stats.average(),
            'bidirectional_median_tls_clump_bytes':           self.bytes_length_stats.median(),
            'bidirectional_stddev_tls_clump_bytes':           self.bytes_length_stats.std_deviation(),
            'bidirectional_variance_tls_clump_bytes':         self.bytes_length_stats.variance(),
            'bidirectional_skew_from_median_tls_clump_bytes': self.bytes_length_stats.skew_from_median(),
            'bidirectional_coeff_of_var_tls_clump_bytes':     self.bytes_length_stats.coeff_of_variation(),
            'bidirectional_min_tls_clump_bytes':              self.bytes_length_stats.min(),
            'bidirectional_max_tls_clump_bytes':              self.bytes_length_stats.max(),
            'bidirectional_mean_tls_clump_sizes':             self.sizes_stats.average(),
            'bidirectional_median_tls_clump_sizes':           self.sizes_stats.median(),
            'bidirectional_stddev_tls_clump_sizes':           self.sizes_stats.std_deviation(),
            'bidirectional_variance_tls_clump_sizes':         self.sizes_stats.variance(),
            'bidirectional_skew_from_median_tls_clump_sizes': self.sizes_stats.skew_from_median(),
            'bidirectional_coeff_of_var_tls_clump_sizes':     self.sizes_stats.coeff_of_variation(),
            'bidirectional_min_tls_clump_sizes':              self.sizes_stats.min(),
            'bidirectional_max_tls_clump_sizes':              self.sizes_stats.max(),
        })
    
    def src2dst_stats(self):
        return pd.Series({
            'src2dst_tls_clumps': len(self.src2dst_lengths),
            'src2dst_mean_tls_clump_bytes':             self.src2dst_bytes_length_stats.average(),
            'src2dst_median_tls_clump_bytes':           self.src2dst_bytes_length_stats.median(),
            'src2dst_stddev_tls_clump_bytes':           self.src2dst_bytes_length_stats.std_deviation(),
            'src2dst_variance_tls_clump_bytes':         self.src2dst_bytes_length_stats.variance(),
            'src2dst_skew_from_median_tls_clump_bytes': self.src2dst_bytes_length_stats.skew_from_median(),
            'src2dst_coeff_of_var_tls_clump_bytes':     self.src2dst_bytes_length_stats.coeff_of_variation(),
            'src2dst_min_tls_clump_bytes':              self.src2dst_bytes_length_stats.min(),
            'src2dst_max_tls_clump_bytes':              self.src2dst_bytes_length_stats.max(),
            'src2dst_mean_tls_clump_sizes':             self.src2dst_sizes_stats.average(),
            'src2dst_median_tls_clump_sizes':           self.src2dst_sizes_stats.median(),
            'src2dst_stddev_tls_clump_sizes':           self.src2dst_sizes_stats.std_deviation(),
            'src2dst_variance_tls_clump_sizes':         self.src2dst_sizes_stats.variance(),
            'src2dst_skew_from_median_tls_clump_sizes': self.src2dst_sizes_stats.skew_from_median(),
            'src2dst_coeff_of_var_tls_clump_sizes':     self.src2dst_sizes_stats.coeff_of_variation(),
            'src2dst_min_tls_clump_sizes':              self.src2dst_sizes_stats.min(),
            'src2dst_max_tls_clump_sizes':              self.src2dst_sizes_stats.max(),
        })
    
    def dst2src_stats(self):
        return pd.Series({
            'dst2src_tls_clumps': len(self.dst2src_lengths),
            'dst2src_mean_tls_clump_bytes':             self.dst2src_bytes_length_stats.average(),
            'dst2src_median_tls_clump_bytes':           self.dst2src_bytes_length_stats.median(),
            'dst2src_stddev_tls_clump_bytes':           self.dst2src_bytes_length_stats.std_deviation(),
            'dst2src_variance_tls_clump_bytes':         self.dst2src_bytes_length_stats.variance(),
            'dst2src_skew_from_median_tls_clump_bytes': self.dst2src_bytes_length_stats.skew_from_median(),
            'dst2src_coeff_of_var_tls_clump_bytes':     self.dst2src_bytes_length_stats.coeff_of_variation(),
            'dst2src_min_tls_clump_bytes':              self.dst2src_bytes_length_stats.min(),
            'dst2src_max_tls_clump_bytes':              self.dst2src_bytes_length_stats.max(),
            'dst2src_mean_tls_clump_sizes':             self.dst2src_sizes_stats.average(),
            'dst2src_median_tls_clump_sizes':           self.dst2src_sizes_stats.median(),
            'dst2src_stddev_tls_clump_sizes':           self.dst2src_sizes_stats.std_deviation(),
            'dst2src_variance_tls_clump_sizes':         self.dst2src_sizes_stats.variance(),
            'dst2src_skew_from_median_tls_clump_sizes': self.dst2src_sizes_stats.skew_from_median(),
            'dst2src_coeff_of_var_tls_clump_sizes':     self.dst2src_sizes_stats.coeff_of_variation(),
            'dst2src_min_tls_clump_sizes':              self.dst2src_sizes_stats.min(),
            'dst2src_max_tls_clump_sizes':              self.dst2src_sizes_stats.max(),
        })
    
    @classmethod
    def available_feature_names(cls):
        return TLSRecordClumpStats(
            pd.DataFrame({
                'tls.record.length': [],
                'direction': [],
                'clump_num' : []
            })
        ).clump_stats().index.to_list()