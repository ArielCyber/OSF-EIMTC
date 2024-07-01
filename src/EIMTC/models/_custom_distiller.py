import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.WARN)  # or any {DEBUG, INFO, WARN, ERROR, FATAL}
from tensorflow.keras.layers import *
from tensorflow.keras.models import *
from tensorflow.python.trackable.data_structures import ListWrapper




class CustomDistiller(Model):
    def __init__(self, modalities=[], adapter_size=128, n_classes=[], merging_method='feat_concat',adapters_setup=[]) -> None:
        super(CustomDistiller, self).__init__()
        self.n_classes = n_classes
        self.modalities = modalities
        self.adapter_size = adapter_size
        self.merging_method = merging_method
        self.adapters_setup = adapters_setup
        self._validate()
        
        
        if self.merging_method == 'feat_concat':
            shared_representation = feat_concat_method(get_sub_adapters(modalities,adapter_size,merging_method,adapters_setup),adapter_size)

        elif self.merging_method == 'deep_concat':
            shared_representation = deep_concat_method(get_sub_adapters(modalities,adapter_size,merging_method,adapters_setup),adapter_size)
            
        elif self.merging_method == 'feat_merge':
            shared_representation = feat_merge_method(get_sub_adapters(modalities,adapter_size,merging_method,adapters_setup),adapter_size)
        
        elif self.merging_method == 'feat_cnn':
            shared_representation = feat_cnn_method(get_sub_adapters(modalities,adapter_size,merging_method,adapters_setup),adapter_size)
        
        outputs = []
        for n_class in n_classes:
            outputs.append(stack([shared_representation] + get_ts_layers(classes_count=n_class, adapter_size=adapter_size)))
        self.model = Model(
            name='CustomDistiller',
            inputs=[modal.input for modal in modalities],
            outputs= outputs
        )
        
        self.pretraining_models = [self.get_model_for_pretraining(modal) for modal in modalities]


    def call(self, inputs, training=None):
        # See: https://www.tensorflow.org/guide/keras/custom_layers_and_models#the_model_class
        return self.model(inputs, training)


    def compile(self, **kwargs):
        self.compile_settings = kwargs
        for model, compile_kwargs in zip(self.pretraining_models + [self.model], zip_dict(kwargs)):
            model.compile(**compile_kwargs)

    def _compile(self, **kwargs): # compile for freezing and unfreezing
        for model, compile_kwargs in zip(self.pretraining_models + [self.model], zip_dict(kwargs)):
            model.compile(**compile_kwargs)

    def fit(self, x, y, **kwargs):
        kwargs_per_fit = list(zip_dict(kwargs))
    
        for features, model, fit_kwargs in zip(x, self.pretraining_models, kwargs_per_fit):
            print('##################### {} ##########################'.format(model.name.upper()))
            model.fit(features, y, **fit_kwargs)

        # FINE-TUNE
        print('##################### FINE-TUNING ##########################')
        fit_kwargs = kwargs_per_fit[len(self.modalities)]
        self.freeze_for_finetuning()
        self.model.fit(x,y, **fit_kwargs)
        self.unfreeze_for_finetuning()

    def fit_display(self, x, y,queue, **kwargs):
        kwargs_per_fit = list(zip_dict(kwargs))
    
        for features, model, fit_kwargs in zip(x, self.pretraining_models, kwargs_per_fit):
            queue.put('##################### {} ##########################'.format(model.name.upper()))
            model.fit(features, y, **fit_kwargs)

        # FINE-TUNE
        queue.put('##################### FINE-TUNING ##########################')
        fit_kwargs = kwargs_per_fit[len(self.modalities)]
        self.freeze_for_finetuning()
        self.model.fit(x,y, **fit_kwargs)
        self.unfreeze_for_finetuning()

    def modals_select_fit(self,x,y,num_modals,to_train=True,**kwargs): # new selected modal allows to choose which modals to pre-train with some modals already pre-train
        kwargs_per_fit = list(zip_dict(kwargs))

        if to_train:
            untrained_modals = [self.pretraining_models[i] for i in num_modals]
        else:
            num_m = []
            for i in range(len(self.pretraining_models)):
                if i not in num_modals:
                    num_m.append(i)
            untrained_modals = [self.pretraining_models[i] for i in num_m]
        
        for features, model, fit_kwargs in zip(x, untrained_modals, kwargs_per_fit):
            print('##################### {} ##########################'.format(model.name.upper()))
            model.fit(features, y, **fit_kwargs)

        # FINE-TUNE
        print('##################### FINE-TUNING ##########################')
        fit_kwargs = kwargs_per_fit[len(self.modalities)]
        self.freeze_for_finetuning()
        self.model.fit(x,y, **fit_kwargs)
        self.unfreeze_for_finetuning()

    def _validate(self):
        # modalities and n_classess array must not be empty .
        assert len(self.modalities) != 0
        assert len(self.n_classes) != 0
        
        # n_classes values must represent the number of classes in each task.
        # and therefore must be positive integers.
        for nclass in self.n_classes:
            assert nclass >= 1
        
        # adapter_size must be positive.
        assert self.adapter_size >= 1


    def get_model_for_pretraining(self, model):
        model_w_adapter = wrap_adapter(model, self.adapter_size)
        outputs = []
        for n_class in self.n_classes:
            outputs.append(stack([model_w_adapter, Dense(n_class, activation='softmax')]))
        return Model(
            name='_'.join(['pretraining_model', model.name.replace(' ','_')]),
            inputs=model.input,
            outputs=outputs
        )


    def freeze_for_finetuning(self):
        for modal in self.modalities:
            for layer in modal.layers:
                layer.trainable = False
        self._compile(**self.compile_settings)


    def unfreeze_for_finetuning(self):
        for modal in self.modalities:
            for layer in modal.layers:
                layer.trainable = True
        self._compile(**self.compile_settings)
        
    



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


def get_adapter_layers(adapter_size):
    return [
        Dropout(0.2),
        Dense(adapter_size),
        ReLU()
    ]


def wrap_adapter(model, adapter_size):
    return stack([model.output, *get_adapter_layers(adapter_size)])


def wrap_adapter_multi(models, adapter_size):
    return [wrap_adapter(model, adapter_size) for model in models]


def get_sr_layers(adapter_size):
    # SR = Shared Representation
    return [
        Dropout(0.2),
        Dense(adapter_size),
        ReLU(),
        Dropout(0.2),
    ]


def get_ts_layers(classes_count, adapter_size):
    # TS = Task Specific
    return [
        Dense(adapter_size),
        ReLU(),
        Dropout(0.2),
        Dense(classes_count),
        Softmax()
    ]
    
def feat_concat_method(modalities,adapter_size):
    return stack(
                [
                    Concatenate()(
                        wrap_adapter_multi(modalities, adapter_size) 
                    )
                ]
                + get_sr_layers(adapter_size)
            )

def deep_concat_method(modalities,adapter_size):
    return stack(
                [
                    Concatenate()(
                        [model.output for model in modalities]
                    )
                ]
                + get_sr_layers(adapter_size)
            )

def feat_merge_method(modalities,adapter_size):
    return stack(
                [
                    Add()(
                        wrap_adapter_multi(modalities, adapter_size) 
                    )
                ]
                + get_sr_layers(adapter_size)
            )
    
def feat_cnn_method(modalities,adapter_size):
    return stack(
        [
                Concatenate()(
                        wrap_adapter_multi(modalities, adapter_size) 
                ),
               Reshape((len(modalities),-1,1)),
               Conv2D(16,3,strides=(1,1),padding="same",activation='relu'),
               MaxPooling2D(3, strides=(3,3),padding="same"),
               Conv2D(32,3,strides=(1,1),padding="same",activation='relu'),
               MaxPooling2D(3, strides=(3,3),padding="same"),
               Conv2D(64,3,strides=(1,1),padding="same",activation='relu'),
               MaxPooling2D(3, strides=(3,3),padding="same"),
               Flatten(),
               Dense(64,activation='relu'),
               Dropout(0.2),
        ]
        + get_sr_layers(adapter_size)
    )
    
def get_sub_adapter(models,adapter_size,merging_method):
    if merging_method == 'deep_concat':
        return Model(
            inputs=[modal.input for modal in models],
            outputs= deep_concat_method(models,adapter_size)
        )
    if merging_method == 'feat_merge':
        return Model(
            inputs=[modal.input for modal in models],
            outputs= feat_merge_method(models,adapter_size)
        )
    if merging_method == 'feat_cnn':
        return Model(
            inputs=[modal.input for modal in models],
            outputs= feat_cnn_method(models,adapter_size)
        )
    return Model(
            inputs=[modal.input for modal in models],
            outputs= feat_concat_method(models,adapter_size)
        )

def get_sub_adapters(models,adapter_size,merging_method,adapters_setup):
    if not adapters_setup:
        return models
    adapters = []
    for adapter in adapters_setup:
        if type(adapter) is ListWrapper:
            adapters.append(get_sub_adapter([models[i] for i in adapter],adapter_size,merging_method))
        else:
            adapters.append(models[adapter])
    return adapters

def zip_dict(d):
    for vals in zip(*(d.values())):
        yield dict(zip(d.keys(), vals))
        