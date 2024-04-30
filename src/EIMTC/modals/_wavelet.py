import pywt
import numpy as np
from ._modal_wrapper import ModalWrapper
from sklearn.ensemble import RandomForestClassifier

class WaveletModality:
    '''
    Wavelet is a deep learning nerual network which uses waves signals with wavelet of the packets flow as input.
    Classifciation type: Time Series
    Input: runs on 15000 miliseconds using time and direction as it features

    Contributor: Natan Dilbary
    '''
    def __init__(self,input_shape) -> None:
        self.model = ModalWrapper(RandomForestClassifier(),name='wavelet modality',input_shape=input_shape)
    
    def fit_transform(self,x):
        return self.transform_signals2Wavelet(x)
    
    def extract_wavelet_features(self,data, features_to_extract=None, wavelet='coif6', level=4):
        # Compute the DWT of your signal
        coeffs = pywt.wavedec(data, wavelet, level=level)
        epsilon = 1e-10  # small constant to avoid division by zero

        feature_map = {
            'mean': lambda x: np.mean(x),
            'std': lambda x: np.std(x),
            'median': lambda x: np.median(x),
            'max': lambda x: np.max(x),
            'min': lambda x: np.min(x),
            'range': lambda x: np.max(x) - np.min(x),
            'energy': lambda x: np.sum(np.square(x)),
            'crest_factor': lambda x: np.max(np.abs(x)) / (np.sqrt(np.mean(np.square(x))) + epsilon),
            'shape_factor': lambda x: np.sqrt(np.mean(np.square(x))) / (np.mean(np.abs(x)) + epsilon),
        }

    # If no features are specified, use all features
        if not features_to_extract:
            features_to_extract = list(feature_map.keys())

        # Compute the requested features
        computed_features = []
        for coeff in coeffs:
            computed_features.extend([feature_map[feat](coeff) for feat in features_to_extract if feat in feature_map])

        # Assemble the feature vector
        feature_vec = np.array(computed_features)
        return feature_vec
    
    def transform_signals2Wavelet(self,signals):
        wavelet_list = []
        for signal in signals:
            features = np.array([self.extract_wavelet_features(signal)])
            wavelet_list.append(features)
        return np.concatenate(wavelet_list)
    
