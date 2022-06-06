import json
import os
from datetime import datetime
from .third_party.tshark.dataframe_utils import add_packet_clump_num_column, add_packet_directions_column, convert_to_correct_dtypes, drop_lengthless_tls_records, get_tls_clump_stats, get_tls_record_stats, groupby_biflows, merge_df_by_biflows, read_tshark_csv_output
from .third_party.tshark.tls_stats import TLSRecordClumpStats, TLSRecordStats
from .third_party.tshark.tshark import run_tshark_tls



'''
Meant to work under linux system.
Tested with WSL ubuntu 18.04.
TShark (Wireshark 3.4.1+)
'''

def extract_tls_features_and_merge(df_nfstream, pcap_filepath, config_filepath,):
    config = _read_config_file(config_filepath)
    tls_features_per_session = _extract_tls_features(pcap_filepath, config['tshark_location'])
    print('Read and merge dataframe of TShark with NFStream', datetime.now().strftime("%H:%M:%S"))
    if tls_features_per_session is None:
        col_names = TLSRecordStats.available_feature_names() + TLSRecordClumpStats.available_feature_names()
        df = df_nfstream.copy()
        df[col_names] = None
    else:
        df = merge_df_by_biflows(tls_features_per_session, df_nfstream)
    print('Exiting 3rd-party: TShark for TLS...', datetime.now().strftime("%H:%M:%S"))
    return df


def _extract_tls_features(pcap_filepath, tshark_location):
    print('Running 3rd-party: Tshark for TLS...', datetime.now().strftime("%H:%M:%S"))
    pcap_file = pcap_filepath
    tshark_output_filepath = 'tshark_outfile.csv'
    run_tshark_tls(pcap_file, tshark_output_filepath, tshark_location)

    print('Reading Tshark CSV output as Pandas Dataframe', datetime.now().strftime("%H:%M:%S"))
    df = read_tshark_csv_output(tshark_output_filepath)
    df = drop_lengthless_tls_records(df)
    if df.empty:
        tls_features_per_session = None
    else:   
        df = convert_to_correct_dtypes(df)
        df = add_packet_directions_column(df)
        df = add_packet_clump_num_column(df)
        record_tls_per_session = get_tls_record_stats(df)
        clump_stats_per_session = get_tls_clump_stats(df)
        tls_features_per_session = record_tls_per_session.join(clump_stats_per_session)

    os.remove(tshark_output_filepath)

    return tls_features_per_session


def _read_config_file(config_filepath):
    print('Reading Configuration...', datetime.now().strftime("%H:%M:%S"))
    print('Configuration at', config_filepath)
    with open(config_filepath) as json_config:
        config = json.load(json_config)
        return config

