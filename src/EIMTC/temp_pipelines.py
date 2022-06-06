from models import DeepMALRawFlows
from temp.n_bytes_per_packet import NBytesPerPacket
from temp.nbytes_plugin import NBytes
from extractor import Extractor
import glob
from models import M1CNN
from os import path, mkdir, stat
import pandas as pd
import numpy as np
import ast
from sklearn.preprocessing import OneHotEncoder



def M1CNNPipeline():
    # 1. Declare PCAP files for feature extraction. - Labels should be on dirs - or filenames
    pcaps_dir_path='./temp/pcap_files_pipeline/'
    csv_storage_location = 'temp'
    features, labels = get_m1cnn_features(csv_storage_location, directory_based_labelling(dir_path=pcaps_dir_path)) 
    # 4. Declare/Create models.
    model = M1CNN(n_classes=len(labels[0]))
    # 5. Train models.
    model.fit(features, labels, epochs=3)

    

def DeepMALPipeline():
    # 1. Declare PCAP files for feature extraction. - Labels should be on dirs - or filenames
    pcaps_dir_path='./temp/pcap_files_pipeline/'
    csv_storage_location = 'temp'
    features, labels = get_deepmal_features(csv_storage_location, directory_based_labelling(dir_path=pcaps_dir_path)) 
    # 4. Declare/Create models.
    model = DeepMALRawFlows(n_classes=len(labels[0]))
    # 5. Train models.
    model.fit(features, labels, epochs=3)


def get_m1cnn_features(csv_storage_location, labelling_method):
    '''
    M1CNN
    '''
    custom_plugin_package = [NBytes()]
    make_dir_if_doesnt_exist(path.join(csv_storage_location, 'm1cnn'))
    extract_features_dir(path.join(csv_storage_location, 'm1cnn'), labelling_method, custom_plugin_package)
    # 3. Read/Load those pcap files to memory 
    return read_all_csvs_in_dir(csv_storage_location)
    

def get_deepmal_features(csv_storage_location, labelling_method):
    '''
    DeepMAL
    '''
    custom_plugin_package = [NBytesPerPacket(100, max_packets=2)]
    make_dir_if_doesnt_exist(path.join(csv_storage_location, 'deepmal'))
    extract_features_dir(path.join(csv_storage_location, 'deepmal'), labelling_method, custom_plugin_package)
    # 3. Read/Load those pcap files to memory 
    return read_all_csvs_in_dir_deepmal(csv_storage_location)


def extract_features_dir(csv_storage_location, labelling_method, custom_plugin_package):
    '''
    General Purpose
    '''
    for pcap_file, label in labelling_method:
        print(pcap_file, label)
        # 2. Extract features for each PCAP file.
        extract_features_pcap_file(pcap_file, csv_storage_location, label, custom_plugin_package)

    
def extract_features_pcap_file(pcap_file, csv_storage_location, label, custom_plugin_package):
    '''
    General Purpose
    '''
    output_dirpath = path.join(csv_storage_location, get_last_dir_in_path(pcap_file))
    if not make_dir_if_doesnt_exist(output_dirpath):
        if compare_last_modified(pcap_file, output_dirpath) == 1:
            print('Skipping feature extraction as CSVs already exist and up-to-date.')
            return
    sessions_csv_filepath = Extractor(pcap_file, output_dirpath, 'tcp or udp', custom_plugin_package).extract()
    # 2.1 add label column
    # Cache? 
    df = pd.read_csv(sessions_csv_filepath)
    df['label'] = np.full(len(df.index), label)
    df.to_csv(sessions_csv_filepath, index=False)
    
    
def read_all_csvs_in_dir(csv_storage_location):
    '''
    M1CNN
    '''
    dfs = []
    for subdir in glob.iglob(path.join(csv_storage_location, '*')):
        for csv_file in glob.iglob(path.join(subdir, '*sessions.csv')):
            dfs.append(pd.read_csv(csv_file, usecols=['udps.n_bytes', 'label']))
    assert (len(dfs) > 0), 'No CSV files were read.'
    df = pd.concat(dfs)
    df['udps.n_bytes'] = df['udps.n_bytes'].apply(ast.literal_eval)
    features = np.stack(df['udps.n_bytes'].values)
    enc = OneHotEncoder(handle_unknown='ignore')
    labels = np.stack(enc.fit_transform(df['label'].values.reshape(-1,1)).toarray())
    
    return features, labels
    
    
def read_all_csvs_in_dir_deepmal(csv_storage_location):
    '''
    deepmal
    '''
    dfs = []
    for subdir in glob.iglob(path.join(csv_storage_location, '*')):
        for csv_file in glob.iglob(path.join(subdir, '*sessions.csv')):
            dfs.append(pd.read_csv(csv_file, usecols=['udps.n_bytes_per_packet', 'label']))
    assert (len(dfs) > 0), 'No CSV files were read.'
    df = pd.concat(dfs)
    df['udps.n_bytes_per_packet'] = df['udps.n_bytes_per_packet'].apply(ast.literal_eval)
    df['udps.n_bytes_per_packet'] = df['udps.n_bytes_per_packet'].apply(np.array, dtype='float32')
    features = np.stack(df['udps.n_bytes_per_packet'].values)
    enc = OneHotEncoder(handle_unknown='ignore')
    labels = np.stack(enc.fit_transform(df['label'].values.reshape(-1,1)).toarray())
    
    return features, labels

    
def directory_based_labelling(dir_path):
    '''
    General Purpose
    '''
    for dir_with_label in glob.iglob(path.join(dir_path, '*')):
        label = get_last_dir_in_path(dir_with_label)
        for pcap_filename in glob.iglob(path.join(dir_with_label, '*.pcap'), recursive=True):
            yield pcap_filename, label


def filename_based_labelling(dir_path, labeller):
    '''
    General Purpose
    '''
    for pcap_filename in glob.iglob(path.join(dir_path, '**', '*.pcap'), recursive=True):
        label = labeller(get_last_dir_in_path(pcap_filename))
        yield pcap_filename, label
            
            
def compare_last_modified(path1, path2):
    last_modified_path1 = stat(path1).st_mtime
    last_modified_path2 = stat(path2).st_mtime
    if last_modified_path1 > last_modified_path2:
        return 0
    else:
        return 1


def make_dir_if_doesnt_exist(dirpath):
    '''
    General Purpose
    '''
    if not path.exists(dirpath):
        try:
            mkdir(dirpath)
            return True
        except:
            print('Error: failed to make a directory with path of', dirpath)
            return False
    return False

def get_last_dir_in_path(dir_path):
    '''
    General Purpose
    '''
    return path.basename(path.normpath(dir_path))
    

#M1CNNPipeline()
DeepMALPipeline()