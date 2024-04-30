from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input,Conv1D,ReLU,MaxPooling1D,Flatten
from ._utils import stack

class WangPayloadModality:
    '''
    WangPayload deep learning nerual network uses for 1D vector input.
    Classifciation type: Payload
    Input: vector 1D of 784 bytes as features.

    Extraction plugin: NBytes

    Paper: "End-to-end Encrypted Traffic Classification with One-dimensional Convolution Neural Networks."
    Authors: Wei Wang, Ming Zhu, Jinlin Wang, Xuewen Zeng, and Zhongzhen Yang.
    '''
    def __init__(self,payload_size=784) -> None:
        input_layer_payload_modality = Input(shape=(payload_size,1), name='input_payload')
        self.model = Model(
            name='Wang payload modality - nbytes',
            inputs=input_layer_payload_modality,
            outputs=stack([
                input_layer_payload_modality,
                Conv1D(16, 25, name='Conv1D_payload_1'),
                ReLU(),
                MaxPooling1D(3, name='MaxPooling1D_payload_1'),
                Conv1D(32, 35, name='Conv1D_payload_2'),
                ReLU(),
                MaxPooling1D(3, name='MaxPooling1D_payload_2'),
                Flatten(), 
            ])
        )