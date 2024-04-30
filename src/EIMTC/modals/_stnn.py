from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input,Lambda,LeakyReLU,Bidirectional,Flatten,Conv2D,MaxPool2D,LSTM,Dense
from tensorflow import expand_dims
from ._utils import stack


class STNNModality:
    '''
    STNN Exteneded deep learning nerual network uses for 2D matrix input.
    Classifciation type: packets and flow statistic
    Input: two-dimensional matrix of 70 features in the shape of 5 x 14.

    Extraction plugin: STNN
    
    Inspired by the paper: "Network Traffic Classifier With Convolutional and Recurrent Neural Networks for Internet of Things"
    '''
    def __init__(self) -> None:
        input_layer_stnn_modality = Input(shape=(5,14), name='input_stnn')
        self.model = Model(
            name='STNN-inspired image modality',
            inputs=input_layer_stnn_modality,
            outputs=stack([
                input_layer_stnn_modality,
                Bidirectional(LSTM(65,return_sequences=True)),
                Lambda(lambda x: expand_dims(x, axis=3)),
                Conv2D(32,3,padding='same'),
                LeakyReLU(),
                Conv2D(32,3,padding='same'),
                LeakyReLU(),
                MaxPool2D(2),
                Conv2D(64,3,padding='same'),
                LeakyReLU(),
                Conv2D(128,3,padding='same'),
                LeakyReLU(),
                MaxPool2D(2),
                Flatten(),
                Dense(512),
            ])
        )
