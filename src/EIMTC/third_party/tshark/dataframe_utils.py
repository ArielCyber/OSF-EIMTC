import pandas as pd
import numpy as np
import ast
from .tls_stats import TLSRecordClumpStats, TLSRecordStats


def merge_df_by_biflows(df_tshark, df_nfstream):
    def add_five_tuple_biflow_id_column_nfstream(df):
        df['five_tuple_biflow_id'] = df.apply(lambda r: sort_key_string(r[['src_ip', 'src_port', 'dst_ip', 'dst_port', 'protocol']]), axis=1)
        return df
    
    df_nfstream = add_five_tuple_biflow_id_column_nfstream(df_nfstream)
    df_tshark = df_tshark.reset_index()
    df_merged = df_nfstream.merge(df_tshark, left_on='five_tuple_biflow_id', right_on='five_tuple_biflow_id', how='left')
    df_merged.drop(columns='five_tuple_biflow_id', inplace=True)
    return df_merged


def read_tshark_csv_output(filepath):
    df = pd.read_csv(filepath, dtype={'tls.record.length': str})
    return df


def get_tls_record_stats(df):
    grouped = groupby_biflows(df)
    return grouped.apply(
        lambda c: TLSRecordStats(
            c[['tls.record.length','direction']].explode('tls.record.length')
        ).length_stats()
    )


def get_tls_clump_stats(df):
    grouped = groupby_biflows(df)
    return grouped.apply(
        lambda g: TLSRecordClumpStats(
            g[['tls.record.length','direction', 'clump_num']].explode('tls.record.length')
        ).clump_stats()
    )
    

def drop_lengthless_tls_records(df):
    '''can happen with tcp restrasnsmission and network errors'''
    return df.dropna(subset=['tls.record.length'])


def convert_to_correct_dtypes(df):
    '''
    tls.record.length can be scalar/list, but it is represented as string at load.
    '''
    if df['tls.record.length'].dtype != 'O':
        # if it contains only scalars, pandas would recognize is the dtype
        # as int64 instead of str/object.
        df['tls.record.length'] = df['tls.record.length'].apply(str)
    df['tls.record.length'] = df['tls.record.length'].apply(ast.literal_eval)
    df['tls.record.length']
    return df


def add_packet_directions_column(df):
    def get_packet_direction(group):
        first_packet = group.iloc[0]
        (src, dst) = first_packet[['ip.src', 'ip.dst']]
        src2dst_packets_indices = group[group['ip.src'] == src].index
        src2dst_packets_direction = np.array([np.zeros(len(src2dst_packets_indices)), src2dst_packets_indices])
        dst2src_packets_indices = group[group['ip.src'] == dst].index
        dst2src_packets_direction = np.array([np.full(len(dst2src_packets_indices), 1), dst2src_packets_indices])
        return pd.Series(
            np.concatenate([src2dst_packets_direction[0], dst2src_packets_direction[0]]), 
            index=np.concatenate([src2dst_packets_direction[1], dst2src_packets_direction[1]])
        )
        
    grouped = groupby_biflows(df)
    directions = grouped.apply(get_packet_direction)
    if directions.index.nlevels == 1:
        ''' if there is only a single session, then pandas
        converts the packet number to columns '''
        directions = directions.iloc[0]
    else: 
        ''' There should be a multindex of fiveuple id string
        along with he packet number, so we remove the fivuple.
        '''
        directions = directions.droplevel(0)
    df['direction'] = directions
    

    return df


def add_packet_clump_num_column(df):
    def get_clump_nums(session):
        clump_nums = []
        df_indices = []
        dir = 0
        begin = 0
        end = 0
        clump_num = 0
        for i, packet in enumerate(session.itertuples()):
            if dir != packet.direction:
                end = i
                clump_nums.extend([clump_num]*(end-begin))
                df_indices.extend(session.index[begin:end])
                begin = end
                dir = packet.direction
                clump_num += 1
        if end <= begin:
            clump_nums.extend([clump_num]*(len(session)-begin))
            df_indices.extend(session.index[begin:])
        return pd.Series(clump_nums, dtype=object, index=df_indices)
    
    grouped = groupby_biflows(df)
    clump_nums = grouped.apply(get_clump_nums)
    if clump_nums.index.nlevels == 1:
        ''' if there is only a single session, then pandas
        converts the packet number to columns '''
        clump_nums = clump_nums.iloc[0]
    else: 
        ''' There should be a multindex of fiveuple id string
        along with he packet number, so we remove the fivuple.
        '''
        clump_nums = clump_nums.droplevel(0)
    df['clump_num'] = clump_nums

    return df


def groupby_biflows(df):
    '''
    TODO: add caching mechanism - groupby is a view of the dataframe.
    '''
    if not 'five_tuple_biflow_id' in df:
        df = add_five_tuple_biflow_id_column(df)
    return df.groupby('five_tuple_biflow_id', sort=False)


def add_five_tuple_biflow_id_column(df):
    df['five_tuple_biflow_id'] = df.apply(lambda r: sort_key_string(r[['ip.src', 'tcp.srcport', 'ip.dst', 'tcp.dstport', 'ip.proto']]), axis=1)
    return df


def sort_key_string(key):
    return '-.'.join(sorted(map(str, key)))



