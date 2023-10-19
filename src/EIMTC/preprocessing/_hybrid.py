        
class HybridPreprocessing:
    @staticmethod
    def preprocess_features(dataframe):
        from EIMTC.plugins.n_bytes import NBytes
        from EIMTC.plugins.protocol_header_fields_extended import ProtocolHeaderFields_Extended
        from EIMTC.plugins.stnn_extended import STNN_Extended
        from EIMTC.plugins.simple_tig import SimpleTIG
        NBytes.preprocess(dataframe)
        ProtocolHeaderFields_Extended.preprocess(dataframe)
        STNN_Extended.preprocess(dataframe)
        SimpleTIG.preprocess(dataframe)