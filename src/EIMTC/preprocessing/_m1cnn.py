        
class M1CNNPreprocessing:
    @staticmethod
    def preprocess_features(dataframe):
        from EIMTC.plugins.n_bytes import NBytes
        NBytes.preprocess(dataframe)
        
