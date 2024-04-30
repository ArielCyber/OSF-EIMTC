from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input,GRU,ReLU,Bidirectional,Flatten
from tensorflow.keras.constraints import max_norm 
from ._utils import stack

class LopezModality:
    '''
    Lopez-Protocol-header-Fields deep learning nerual network uses for Packet Header Fields vector input.
    Classifciation type: Packet Header Fields
    Input: two-dimensional vector of number of packets and 4 features from each packet.

    Extraction plugin: ProtocolHeaderFields
    
    The paper: "Network Traffic Classifier With Convolutional and Recurrent Neural Networks for Internet of Things"
    '''
    def __init__(self,packet_count=32) -> None:
        input_layer_protocol_fields_modality = Input(shape=(packet_count,4), name='input_protocol_fields')
        self.model = Model(
            name='Lopez protocol header fields modality',
            inputs=input_layer_protocol_fields_modality,
            outputs=stack([
                input_layer_protocol_fields_modality,
                Bidirectional(GRU(64, return_sequences=True, kernel_constraint=max_norm(3))),
                ReLU(),
                Flatten(),
            ])
        )
