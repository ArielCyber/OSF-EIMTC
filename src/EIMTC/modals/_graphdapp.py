from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input,Layer,Concatenate,Dense,BatchNormalization,Dropout
from tensorflow.keras import activations
import tensorflow as tf

class GraphDAppModality:
    '''
    GraphDApp deep learning nerual network uses for Graph input.
    Classifciation type: Graphs
    Input: vector of two values an adjacent matrix and a node feature vector.

    Extraction plugin: SimpleTIG

    Paper: "Accurate Decentralized Application Identification via Encrypted Traffic Analysis Using Graph Neural Networks."
    Authors: Meng Shen, Jinpeng Zhang, Liehuang Zhu, Ke Xu, and Xiaojiang Du.
    
    '''
    def __init__(self,n_packets=32) -> None:
        input_layer_graphdapp_adj_matrix_modality = Input(shape=(n_packets,n_packets),name='input_graphdapp_adj_matrix')
        input_layer_graphdapp_features_modality = Input(shape=(n_packets,1),name='input_graphdapp_features')
        inputs_layer = [input_layer_graphdapp_adj_matrix_modality, input_layer_graphdapp_features_modality]
        mlp1 = MLPLayer(64)
        mlp2 = MLPLayer(64)
        mlp3 = MLPLayer(64)
        readout = Readout()
        concat = Concatenate()
        x1 = mlp1(inputs_layer)
        x2 = mlp2(x1)
        x3 = mlp3(x2)
        x4 = readout([x1, x2, x3])
        x4 = concat(x4)
        self.model = Model(
            name='GraphDApp modality',
            inputs=inputs_layer,
            outputs= x4
        )

class Readout(Layer):
    def __init__(self):
        super(Readout, self).__init__()
    
    def call(self, inputs):
        FsBatch = []
        for i in range(len(inputs)):
            Fbatch = inputs[i][1]
            FsBatch.append(tf.reduce_sum(Fbatch, axis=-2))
        return FsBatch


class MLPLayer(Layer):
    def __init__(
            self, 
            output_size=5, 
            activation='relu', 
            use_bias=True, 
            neighbour_agg_method='sum', 
            dropout_rate=0.025):
        super(MLPLayer, self).__init__()
        self.output_size = output_size
        self.dense = Dense(self.output_size, use_bias=use_bias)
        self.activation = activations.get(activation)
        self.batch_norm = BatchNormalization()
        self.dropout = Dropout(dropout_rate)
    
    def build(self, input_shape):
        self.eps = self.add_weight(
            name='epsilon',
            shape=(1,),
            initializer="random_normal",
            dtype='float32',
            trainable=True,
        )
    
    def call(self, inputs, training=False):
        '''
        [A, F]
        '''
        A = inputs[0]
        F = inputs[1]
        outputs = tf.multiply(1.0+self.eps, F) + tf.matmul(A,F)
        outputs = self.dense(outputs)
        outputs = self.activation(outputs)
        outputs = self.batch_norm(outputs, training=training)
        outputs = self.dropout(outputs)
        return [A, outputs]
