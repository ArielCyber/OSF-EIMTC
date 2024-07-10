import numpy as np
import pandas as pd
from .stnn_extended import STNNExtended
from .tdl import TDL

class STNNFT():
    ''' STNNFT |
    Extracts 140 features from `n_packets` packets. The extended version
    maintain only flow direction statistical features src2dst, dst2src the same and
    for the bidectional take only the packets,bytes,packets per second and bytes per second.
    Which are total of 32 features. In addition added 108 new features from clumps flow 84 feautres
    and from packet size and inter-arrival-time bidrectional flow 24 features a total of 140 features.
    added an additional feature of Flow Time.
    
    Feature Outputs:
        - udps.stnn_f_t: output shape of (141).
    '''

    def plugins(n_packets):
        return STNNExtended.plugins(n_packets),TDL(n_packet=n_packets)
    
    @staticmethod
    def stnn_ft(row):
        STNNExtended.stnn_feat_enh(row)
        return np.append(row['udps.stnn_image_enh'],[row['udps.port_TDL'][-1][0]-row['udps.port_TDL'][0][0]])
        
    @staticmethod
    def preprocess(dataframe: pd.DataFrame):
        STNNExtended.preprocess(dataframe)

        dataframe['udps.stnn_f_t'] = dataframe.apply(STNNFT.stnn_ft,axis=1) 
