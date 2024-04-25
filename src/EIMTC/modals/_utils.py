import pandas as pd
import numpy as np

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

def create_signal(timestamp,direction,packetsize,relativetime):
    df = pd.DataFrame({'Timestamp':timestamp,'Direction':direction,'PacketSize':packetsize,'RelativeTime':relativetime})
    df['Milliseconds'] = df['RelativeTime'].round().astype(int)
    grouped = df.groupby('Milliseconds').apply(lambda x: x['Direction'].astype(int).sum()).astype(int)
    ms_series = pd.Series(np.zeros(15000, dtype=int), index=np.arange(15000))
    ms_series.update(grouped)
    return np.stack(ms_series.values.tolist())