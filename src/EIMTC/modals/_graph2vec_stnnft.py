from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input,Dense,Dropout,Concatenate,BatchNormalization

class G2VSTNNFTModality:
    '''
    G2V deep learning nerual network uses for Graph input with STNNFT (statistical) input.
    Classifciation type: Graphs
    Input: Graph2Vec vector 1-dimension matching the input shape of the model and STNNFT vector 1-dimension.

    By the paper: "ETCG2vec: Encrypted Traffic Classification in Real-World Scenarios Using Multimodal Graph-Based Embeddings "
    Authors: Revital Marbel, Chen Hajaj, Amit Dvir, Adi Lichy
    '''
    def __init__(self,input_shape,input_shape_stnnft=(141,)) -> None:
        self.model = _G2VSTNNFT_Model(input_shape,input_shape_stnnft)



class _G2VSTNNFT_Model(Model):
    def __init__(self,input_shape,input_shape_stnnft) -> None:
        super(_G2VSTNNFT_Model, self).__init__(name="Graph2Vec-STNNFT_modality")

        #Layers
        self.input_vector_graph_layer = Input(shape=input_shape,name=f'input_vector_graph_STNNFT')
        self.input_stnnft_layer = Input(shape=input_shape_stnnft,name=f'input_STNNFT')
        self.batchnorm_g2v = BatchNormalization()
        self.dense = Dense(128,activation='relu')
        self.dropout = Dropout(0.2)
        self.dense_2 = Dense(128,activation='relu')
        self.dropout_2 = Dropout(0.2)
        self.norm_batch_stnnft = BatchNormalization()
        self.concat = Concatenate()
        self(inputs=[self.input_vector_graph_layer,self.input_stnnft_layer])


    def call(self,inputs):
        g2v_norm = self.batchnorm_g2v(inputs[0])
        dense_out =  self.dense(g2v_norm)
        dropout_out = self.dropout(dense_out)
        dense_out_2 = self.dense_2(dropout_out)
        dropout_out_2 = self.dropout_2(dense_out_2)
        batch_norm_out  = self.norm_batch_stnnft(inputs[1])
        concat_out = self.concat([dropout_out_2,batch_norm_out])
        return concat_out