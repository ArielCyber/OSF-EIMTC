        
class HybridPreprocessing:
    @staticmethod
    def preprocess_features(dataframe):
        from EIMTC.plugins.n_bytes import NBytes
        from EIMTC.plugins.protocol_header_fields_extended import ProtocolHeaderFieldsExtended
        from EIMTC.plugins.stnn_extended import STNNExtended
        from EIMTC.plugins.simple_tig import SimpleTIG
        NBytes.preprocess(dataframe)
        ProtocolHeaderFieldsExtended.preprocess(dataframe)
        STNNExtended.preprocess(dataframe)
        SimpleTIG.preprocess(dataframe)