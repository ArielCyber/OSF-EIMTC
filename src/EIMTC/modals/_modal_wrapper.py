import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Layer, BatchNormalization, ReLU, Dense,  Dropout

class ModalWrapper(tf.keras.Model):
    '''
    ModelWrapper is a deep learning nerual network given a inner model to train and learn on.
    Classifciation type: Any
    Input: changes by the inner model

    Contributor: Adi Lichy
    '''
    def __init__(self,inner_model,name,input_shape=None,deep_model=None,units=128,dropout_rate=0.2):
        super(ModalWrapper, self).__init__(name=name)
        self.inner_model = inner_model
        self.input_shape_wrapper = input_shape
        self.deep_model = deep_model
        self._validate()
        # Layers
        if self.prebuilt_layers:
            self.input_layer = Input(shape=self.input_shape_wrapper,name=f'input_{name.replace("_modality","")}')
            self.dense1 = Dense(units)
            self.activation1 = ReLU()
            self.batch_norm1 = BatchNormalization()
            self.dropout1 = Dropout(dropout_rate)
            self.dense2 = Dense(units)
            self.activation2 = ReLU()
            self.batch_norm2 = BatchNormalization()
            self.dropout2 = Dropout(dropout_rate)
            self(inputs=self.input_layer)
        else:
            self(inputs=deep_model.inputs)


    # validating modal parameters
    def _validate(self):

        assert hasattr(self.inner_model,'fit') # must have fit to pass the data

        if hasattr(self.inner_model,'predict'):
            self.is_classifer = True
        else:
            self.is_classifer = False

        assert not (self.input_shape_wrapper is None and self.deep_model is None) # check for nerual network build

        if self.input_shape_wrapper is not None:
            self.prebuilt_layers = True
        else:
            self.prebuilt_layers = False

    def fit_wrapper_model(self,x,y=None):
        if y is not None:
            self.inner_model.fit(x,y)
        else:
            self.inner_model.fit(x)
    
    def predict_wrapper_model(self,x):
        return self.inner_model.predict(x)

    def call(self,inputs):
        if self.prebuilt_layers:
            dense1_out = self.dense1(inputs)
            acti1_out = self.activation1(dense1_out)
            norm1_out = self.batch_norm1(acti1_out)
            dropout1_out = self.dropout1(norm1_out)
            dense2_out = self.dense2(dropout1_out)
            acti2_out = self.activation2(dense2_out)
            norm2_out = self.batch_norm2(acti2_out)
            dropout2_out = self.dropout2(norm2_out)
            return  dropout2_out
        else:
            return self.deep_model(inputs)
    
    def fit(self,x=None,y=None,**kwargs):
        if self.is_classifer:
            print('Inner model fit...')
            self.fit_wrapper_model(x,y)
            inner_model_x = np.stack(self.predict_wrapper_model(x))
        else:
            print('Inner model fit...')
            inner_model_x = self.fit_wrapper_model(x)
        print('Deep model fit...')
        return super(ModalWrapper,self).fit(inner_model_x,np.stack(y),**kwargs)
    
    def predict(self,x,**kwargs):
        if self.is_classifer:
            inner_model_x = np.stack(self.predict_wrapper_model(x))
        else:
            inner_model_x = self.fit_wrapper_model(x)
        return super(ModalWrapper,self).predict(inner_model_x,**kwargs)