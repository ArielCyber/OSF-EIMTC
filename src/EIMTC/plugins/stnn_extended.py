from EIMTC.plugins import stnn, clump_flows, packets_size_interarrival_time
import pandas  as pd
import numpy as np

class STNN_Extended():
    ''' STNN_Extended |
    Extracts 149 features from `n_packets` packets. The extended version
    maintain only flow direction statistical features bidirectional, src2dst, dst2src. Which are total of 42 features.
    and added 107 new features from clump flows with a total of 149 features.
    
    Feature Outputs:
        - udps.stnn_image_enh: output shape of (149).
    '''
    size_iat_cols = [
            'udps.packets_size_max', 'udps.packets_size_stddev',
            'udps.packets_size_first_quartile',
            'udps.packets_size_second_quartile',
            'udps.packets_size_third_quartile', 'udps.packets_size_mean',
            'udps.packets_size_median_absoulte_deviation',
            'udps.packets_size_variance', 'udps.packets_size_skewness',
            'udps.packets_size_kurtosis', 'udps.packets_size_sum',
            'udps.packets_interarrival_time_min',
            'udps.packets_interarrival_time_max',
            'udps.packets_interarrival_time_stddev',
            'udps.packets_interarrival_time_first_quartile',
            'udps.packets_interarrival_time_second_quartile',
            'udps.packets_interarrival_time_third_quartile',
            'udps.packets_interarrival_time_mean',
            'udps.packets_interarrival_time_median_absoulte_deviation',
            'udps.packets_interarrival_time_variance',
            'udps.packets_interarrival_time_skewness',
            'udps.packets_interarrival_time_kurtosis',
            'udps.packets_interarrival_time_sum'
        ]

    clump_cols = ['udps.src2dst_max_clumps_len',
        'udps.src2dst_min_clumps_len',
        'udps.src2dst_mean_clumps_len',
        'udps.src2dst_stddev_clumps_len',
        'udps.src2dst_skewness_clumps_len',
        'udps.src2dst_variance_clumps_len',
        'udps.src2dst_kurtosis_clumps_len',
        'udps.src2dst_max_clumps_size',
        'udps.src2dst_min_clumps_size',
        'udps.src2dst_mean_clumps_size',
        'udps.src2dst_stddev_clumps_size',
        'udps.src2dst_skewness_clumps_size',
        'udps.src2dst_variance_clumps_size',
        'udps.src2dst_kurtosis_clumps_size',
        'udps.src2dst_max_clumps_bytes_per_packet',
        'udps.src2dst_min_clumps_bytes_per_packet',
        'udps.src2dst_mean_clumps_bytes_per_packet',
        'udps.src2dst_stddev_clumps_bytes_per_packet',
        'udps.src2dst_skewness_clumps_bytes_per_packet',
        'udps.src2dst_variance_clumps_bytes_per_packet',
        'udps.src2dst_kurtosis_clumps_bytes_per_packet',
        'udps.src2dst_max_clumps_interarrival_time',
        'udps.src2dst_min_clumps_interarrival_time',
        'udps.src2dst_mean_clumps_interarrival_time',
        'udps.src2dst_stddev_clumps_interarrival_time',
        'udps.src2dst_skewness_clumps_interarrival_time',
        'udps.src2dst_variance_clumps_interarrival_time',
        'udps.src2dst_kurtosis_clumps_interarrival_time',
        'udps.dst2src_max_clumps_len',
        'udps.dst2src_min_clumps_len',
        'udps.dst2src_mean_clumps_len',
        'udps.dst2src_stddev_clumps_len',
        'udps.dst2src_skewness_clumps_len',
        'udps.dst2src_variance_clumps_len',
        'udps.dst2src_kurtosis_clumps_len',
        'udps.dst2src_max_clumps_size',
        'udps.dst2src_min_clumps_size',
        'udps.dst2src_mean_clumps_size',
        'udps.dst2src_stddev_clumps_size',
        'udps.dst2src_skewness_clumps_size',
        'udps.dst2src_variance_clumps_size',
        'udps.dst2src_kurtosis_clumps_size',
        'udps.dst2src_max_clumps_bytes_per_packet',
        'udps.dst2src_min_clumps_bytes_per_packet',
        'udps.dst2src_mean_clumps_bytes_per_packet',
        'udps.dst2src_stddev_clumps_bytes_per_packet',
        'udps.dst2src_skewness_clumps_bytes_per_packet',
        'udps.dst2src_variance_clumps_bytes_per_packet',
        'udps.dst2src_kurtosis_clumps_bytes_per_packet',
        'udps.dst2src_max_clumps_interarrival_time',
        'udps.dst2src_min_clumps_interarrival_time',
        'udps.dst2src_mean_clumps_interarrival_time',
        'udps.dst2src_stddev_clumps_interarrival_time',
        'udps.dst2src_skewness_clumps_interarrival_time',
        'udps.dst2src_variance_clumps_interarrival_time',
        'udps.dst2src_kurtosis_clumps_interarrival_time',
        'udps.max_clumps_len',
        'udps.min_clumps_len',
        'udps.mean_clumps_len',
        'udps.stddev_clumps_len',
        'udps.skewness_clumps_len',
        'udps.variance_clumps_len',
        'udps.kurtosis_clumps_len',
        'udps.max_clumps_size',
        'udps.min_clumps_size',
        'udps.mean_clumps_size',
        'udps.stddev_clumps_size',
        'udps.skewness_clumps_size',
        'udps.variance_clumps_size',
        'udps.kurtosis_clumps_size',
        'udps.max_clumps_bytes_per_packet',
        'udps.min_clumps_bytes_per_packet',
        'udps.mean_clumps_bytes_per_packet',
        'udps.stddev_clumps_bytes_per_packet',
        'udps.skewness_clumps_bytes_per_packet',
        'udps.variance_clumps_bytes_per_packet',
        'udps.kurtosis_clumps_bytes_per_packet',
        'udps.max_clumps_interarrival_time',
        'udps.min_clumps_interarrival_time',
        'udps.mean_clumps_interarrival_time',
        'udps.stddev_clumps_interarrival_time',
        'udps.skewness_clumps_interarrival_time',
        'udps.variance_clumps_interarrival_time',
        'udps.kurtosis_clumps_interarrival_time']



    def plugins(n_packets=32):
        return clump_flows.Clump_Flow(n_packets),stnn.STNN(n_packets),packets_size_interarrival_time.Packets_size_and_interarrival_time(n_packets)

    @staticmethod
    def stnn_feat_enh(row):

        feat = row[STNN_Extended.size_iat_cols + STNN_Extended.clump_cols]
        sub_stnn =  np.asarray(row['udps.stnn_image'][1:3]).flatten()
        return np.concatenate([sub_stnn, feat]).astype('float32')

            
    @staticmethod
    def preprocess(dataframe: pd.DataFrame):
        ''' 
        Preprocessing method for the STNN extended features.
        Converting 'udps.stnn_image_enh' column from str to 1D-list.
        import
        '''
        # validate
        stnn.STNN.preprocess(dataframe)

        dataframe['udps.stnn_image_enh'] = dataframe.apply(STNN_Extended.stnn_feat_enh,axis=1)
    