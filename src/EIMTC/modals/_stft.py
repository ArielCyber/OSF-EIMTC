import librosa
import scipy
import numpy as np
from ._modal_wrapper import ModalWrapper
from sklearn.ensemble import RandomForestClassifier

class STFTModality:
    '''
    STFT is a deep learning nerual network which uses waves signals with short-time-fourier-transform (STFT) of the packets flow as input.
    Classifciation type: Time Series
    Input: runs on 15000 miliseconds using time and direction as it features

    Contributor: Natan Dilbary
    '''
    def __init__(self,input_shape) -> None:
        self.model = ModalWrapper(RandomForestClassifier(),name='short-time-fourier-transform modality',input_shape=input_shape)

    def fit_transform(self,x):
        return self.transform_signals2STFT(x)
    
    def extract_STFT(self,data,features_to_extract=None):
        # Compute the STFT of the signal
        f, t, Zxx = scipy.signal.stft(data, fs=1000, window='hann', nperseg=256, noverlap=128)
        # Compute the magnitude spectrogram
        mag_spectrogram = np.abs(Zxx)

        # If no features are specified, use default features
        if features_to_extract is None:
            features_to_extract = ('mean', 'std', 'spectral_centroid',
                                'spectral_bandwidth', 'spectral_contrast',
                                'spectral_flatness','spectral_rolloff', 'chroma_stft', 'mfcc')

        feature_map = {
            'mean': lambda: np.mean(mag_spectrogram, axis=1),
            'std': lambda: np.std(mag_spectrogram, axis=1),
            'spectral_centroid': lambda: librosa.feature.spectral_centroid(S=mag_spectrogram)[0],
            'spectral_bandwidth': lambda: librosa.feature.spectral_bandwidth(S=mag_spectrogram)[0],
            'spectral_contrast': lambda: librosa.feature.spectral_contrast(S=mag_spectrogram)[0],
            'spectral_flatness': lambda: librosa.feature.spectral_flatness(S=mag_spectrogram)[0],
            'spectral_rolloff': lambda: librosa.feature.spectral_rolloff(S=mag_spectrogram, sr=1000)[0],
            'chroma_stft': lambda: librosa.feature.chroma_stft(S=mag_spectrogram, sr=1000)[0],
            'mfcc': lambda: librosa.feature.mfcc(S=mag_spectrogram, sr=1000)[0]
        }
        
        # Compute the requested features
        computed_features = [feature_map[feat]() for feat in features_to_extract if feat in feature_map]

        # Combine all computed features into one vector
        feature_vec = np.concatenate(computed_features)
        return feature_vec
    
    def transform_signals2STFT(self,signals):
        stft_list = []
        for signal in signals:
            features = np.array([self.extract_STFT(signal)])
            stft_list.append(features)
        return np.concatenate(stft_list)
    