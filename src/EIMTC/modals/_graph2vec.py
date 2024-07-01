from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input,Dense,Dropout

class G2VModality:
    '''
    G2V deep learning nerual network uses for Graph input.
    Classifciation type: Graphs
    Input: Graph2Vec vector 1-dimension matching the input shape of the model

    Graph2Vec algorithm can be found in preprocess

    Inspired by the paper: " graph2vec: Learning Distributed Representations of Graphs "
    Authors: Narayanan, Annamalai and Chandramohan, Mahinthan and Venkatesan, Rajasekar and Chen, Lihui and Liu, Yang and Jaiswal, Shantanu
    '''
    def __init__(self,input_shape) -> None:
        self.model = _G2V_Model(input_shape)



class _G2V_Model(Model):
    def __init__(self,input_shape) -> None:
        super(_G2V_Model, self).__init__(name="Graph2Vec_modality")

        #Layers
        self.input_layer = Input(shape=input_shape,name=f'input_vector_graph')
        self.dense = Dense(128,activation='relu')
        self.dropout = Dropout(0.2)
        self.dense_2 = Dense(128,activation='relu')
        self.dropout_2 = Dropout(0.2)
        self(inputs=self.input_layer)


    def call(self,inputs):
        dense_out =  self.dense(inputs)
        dropout_out = self.dropout(dense_out)
        dense_out_2 = self.dense_2(dropout_out)
        dropout_out_2 = self.dropout_2(dense_out_2)
        return dropout_out_2
