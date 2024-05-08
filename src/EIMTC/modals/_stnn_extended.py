from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input,LeakyReLU,Bidirectional,Flatten,Conv1D,MaxPool1D,LSTM,Dense
from ._utils import stack

class STNNExtendedModality:
    '''
    STNN Exteneded deep learning nerual network uses for 1D vector input.
    Classifciation type: packets and flow statistic
    Input: one-dimensional vector of 140 features.

    Extraction plugin: STNNExtended
    
    Inspired by the paper: "Network Traffic Classifier With Convolutional and Recurrent Neural Networks for Internet of Things"
    '''
    def __init__(self) -> None:
        input_layer_stnn_modality = Input(shape=(140,1), name='input_stnn')
        self.model = Model(
            name='STNN-inspired image extended modality',
            inputs=input_layer_stnn_modality,
            outputs=stack([
                input_layer_stnn_modality,
                Bidirectional(LSTM(64,return_sequences=True)), #128
                Conv1D(32,3,padding='same'),
                LeakyReLU(),
                #Conv1D(32,3,padding='same'),
                #LeakyReLU(),
                #MaxPool1D(2),
                Conv1D(64,3,padding='same'),
                LeakyReLU(),
                #Conv1D(128,3,padding='same'),
                #LeakyReLU(),
                MaxPool1D(2),
                Flatten(),
                Dense(512),
            ])
        )
