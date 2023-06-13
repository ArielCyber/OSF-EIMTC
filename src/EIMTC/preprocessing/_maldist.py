        
class MalDistPreprocessing:
    @staticmethod
    def preprocess_features(dataframe):
        from EIMTC.plugins.n_bytes import NBytes
        from EIMTC.plugins.protocol_header_fields import ProtocolHeaderFields
        from EIMTC.plugins.stnn import STNN
        NBytes.preprocess(dataframe)
        ProtocolHeaderFields.preprocess(dataframe)
        STNN.preprocess(dataframe)