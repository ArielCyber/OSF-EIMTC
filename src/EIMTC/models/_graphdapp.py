from tensorflow.keras.models import Model
from tensorflow.keras.layers import Layer, BatchNormalization, Concatenate, Dropout, Dense, Softmax
from tensorflow.keras import activations
import tensorflow as tf


class GraphDApp(Model):
    '''
    # GraphDApp Model
    ## Parameters
    
    - `n_classes` (int): Number of possible classes an input can be classified into (#units in final dense layer). 
    - `mlplayer_units` (int): Number of units in each single-MLP layer.
    
    ## Input
    ### Per sample
    - Graph adjacancy matrix
        - Shape: (n_nodes, n_nodes)
    - Node features
        - Shape: (n_nodes, n_features_per_node)
    
    ### Final input shape
    [(n_samples, n_nodes, n, nodes), (n_samples, n_nodes, n_features_per_node)]
    
    
    ## Paper
    
    "Accurate Decentralized Application Identification via Encrypted Traffic Analysis Using Graph Neural Networks,"
    
    ### By
    
    - Meng Shen.
    - Jinpeng Zhang.
    - Liehuang Zhu.
    - Ke Xu.
    - Xiaojiang Du.
    '''
    def __init__(
            self, 
            n_classes, 
            mlplayer_units=64, 
            neighbour_agg_method='sum', 
            **kwargs):
        super(GraphDApp, self).__init__(**kwargs)
        self.mlp1 = MLPLayer(mlplayer_units)
        self.mlp2 = MLPLayer(mlplayer_units)
        self.mlp3 = MLPLayer(mlplayer_units)
        self.readout = Readout()
        self.concat = Concatenate()
        self.dense = Dense(n_classes)
        self.classification = Softmax()
    
    def call(self, inputs):
        x1 = self.mlp1(inputs)
        x2 = self.mlp2(x1)
        x3 = self.mlp3(x2)
        x4 = self.readout([x1, x2, x3])
        x4 = self.concat(x4)
        x4 = self.dense(x4)
        return self.classification(x4)


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