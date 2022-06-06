import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.WARN)  # or any {DEBUG, INFO, WARN, ERROR, FATAL}
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout, Input, BatchNormalization
from tensorflow.keras.models import Model
import tensorflow.keras as K




class DeepMALRawFlows(Model):
    def __init__(self, payload_size=100, packet_count=2, n_classes=2) -> None:
        super(DeepMALRawFlows, self).__init__()
        input_layer = Input(shape=(packet_count, payload_size))
        self.model = Model(
            name='DeepMAL-Flows',
            inputs=input_layer,
            outputs=stack([
                input_layer, # first layer
                BatchNormalization(),
                Conv1D(32, 5, padding="same"), # second layer...
                Flatten(),
                Dense(50, activation='relu'),
                Dropout(0.2),
                Dense(100, activation='relu'),
                Dropout(0.2),
                Dense(n_classes, activation='softmax') 
            ])
        )

        '''
        optimizer='adam',
        loss=tf.keras.losses.CategoricalCrossentropy(),
        '''
    
    
    def call(self, inputs, training=None):
        # See: https://www.tensorflow.org/guide/keras/custom_layers_and_models#the_model_class
        return self.model(inputs, training)



###################
# Model utilities #
###################

def stack(layers):
    '''
    Using the Functional-API of Tensorflow to build a sequential
    network (stacked layers) from list of layers.
    '''
    layer_stack = None
    for layer in layers:
        if layer_stack is None:
            layer_stack = layer
        else:
            layer_stack = layer(layer_stack)
    return layer_stack