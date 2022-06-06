import numpy as np
from tensorflow.keras import activations
import tensorflow as tf
import tensorflow.keras as tfk


class ChainedGNN(tfk.Model):
    '''
    ## Paper
    
    "CGNN: Traffic Classification with Graph Neural Network"
    ### By
    - Bo Pang.
    - Yongquan Fu.
    - Siyuan Ren.
    - Ye Wang.
    - Qing Liao.
    - Yan Jia.
    '''
    def __init__(self, n_classes, use_precomputed_norm_adj_mat=True):
        super(ChainedGNN, self).__init__()
        self.use_precomputed_norm_adj_mat = use_precomputed_norm_adj_mat
        self.sgc1 = SGCLayer(516, 1, 'relu', use_precomputed_norm_adj_mat=use_precomputed_norm_adj_mat)
        self.sgc2 = SGCLayer(256, 1, 'relu', use_precomputed_norm_adj_mat=use_precomputed_norm_adj_mat)
        self.dense = tfk.layers.Dense(n_classes)

    def call(self, inputs):
        '''
        x = [A, F] or F. Depends on use_precomputed_norm_adj_mat
        '''
        x = self.sgc1(inputs)
        x = self.sgc2(x)
        if self.use_precomputed_norm_adj_mat:
            F = tf.expand_dims(x, -1)
        else:
            F = tf.expand_dims(x[1], -1)
        x = tfk.layers.AveragePooling2D(strides=1, pool_size=(F.shape[1],1))(F)
        x = tf.squeeze(x, [1, -1])
        x = self.dense(x)
        x = tf.nn.softmax(x)
        return x


class SGCLayer(tfk.layers.Layer):
    '''
    Simple Graph Convolution (SGC) Layer
    '''
    def __init__(self, outputsNumber, neighbourhood_distance=1, activation=None, use_precomputed_norm_adj_mat=True):
        super(SGCLayer, self).__init__()
        self.outputs = outputsNumber
        self.S = None # local normalized adj matrix
        self.neighbourhood_distance = neighbourhood_distance
        self.activation = activations.get(activation)
        self.use_precomputed_norm_adj_mat = use_precomputed_norm_adj_mat

    def build(self, input_shape):
        if self.use_precomputed_norm_adj_mat:
            node_feature_length = input_shape[-1]
            self.S = tf.Variable(
                initial_value=np.linalg.matrix_power(
                    getS(input_shape[1]), 
                    self.neighbourhood_distance
                ), 
                trainable=False,
                name='Normalized Adj. Matrix'
            )
        else: 
            node_feature_length = input_shape[1][-1]
            
        self.teta = self.add_weight(
            "teta",
            shape=[node_feature_length, self.outputs],
            trainable=True,
            initializer="random_normal"
        )
            
    def call(self, inputs):
        if self.use_precomputed_norm_adj_mat:
            return self._call_without_adj(inputs)
        else:
            return self._call_with_adj(inputs)
        
    def _call_with_adj(self, inputs):
        A = inputs[0]
        S = norm_adj_matrix(inputs[0])
        F = inputs[1] # Node features matrix
        F = self._call_work_node_features(S, F)
        
        return [A, F]
    
    def _call_without_adj(self, inputs):
        S = self.S
        F = inputs # Node features matrix
        F = self._call_work_node_features(S, F)
        
        return F
        
    def _call_work_node_features(self, S, F):
        F = tf.matmul(S, F)
        F = tf.matmul(F, self.teta)
        if self.activation is not None:
            F = self.activation(F)
        
        return F


def getS(n):
    # By itay and Omer
    # source: https://github.com/itay74121/GNN/blob/master/CGNN/CGNN.py
    if n == 1:
        return np.array(0)
    if n == 2:
        return np.array([(0, 1),(1, 0)])
    S = np.zeros((n,n), dtype='float32')
    S[0,0], S[n - 1,n - 1] = 0.50000, 0.50000 # first and last vertices with self loop
    S[0,1], S[1,0], S[n - 2,n - 1], S[n - 1,n - 2] = 0.40825, 0.40825, 0.40825, 0.40825 # first and last vertices with other edges
    S[1,1], S[1,2], S[n - 2,n - 2], S[n - 2,n - 3] = 0.33333, 0.33333, 0.33333, 0.33333 # rest connected to first and last
    for i in range(2, len(S) - 2): # rest of vertices
        for j in range(i - 1, i + 2):
            S[i,j] = 0.33333
    return S


def norm_adj_matrix(adj_batch, add_self_loops=True):
    # source: https://github.com/stellargraph/stellargraph/blob/5ca1e59e91cb6ac470bf19ff3da39b3a1a68650e/stellargraph/core/utils.py
    # Add self loops.
    if add_self_loops:
        adj_batch = adj_batch + tf.linalg.diag(tf.ones(adj_batch.shape[1]) - tf.linalg.diag_part(adj_batch))

    # Normalization
    rowsum = tf.reduce_sum(adj_batch, 1)
    d_mat_inv_sqrt = tf.linalg.diag(tf.math.rsqrt(rowsum))
    adj_normalized = tf.matmul(tf.matmul(d_mat_inv_sqrt, adj_batch), d_mat_inv_sqrt)
    
    return adj_normalized