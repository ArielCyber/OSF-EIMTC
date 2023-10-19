import numpy as np
from sklearn.preprocessing import OneHotEncoder


class OneHotEncoderEIMTC:
    def __init__(self,  **kwargs) -> None:
        self._inner_ohc = OneHotEncoder(**kwargs)

    @property
    def infrequent_categories_(self):
        return self._inner_ohc.infrequent_categories_
    
    @property
    def categories_(self):
        return self._inner_ohc.categories_[0]
    
    @property
    def drop_idx_(self):
        return self._inner_ohc.drop_idx_
    
    @property
    def n_features_in_(self):
        return self._inner_ohc.n_features_in_
    
    @property
    def feature_names_in_(self):
        return self._inner_ohc.feature_names_in_
    
    def fit(self, X, y=None):
        X = np.asarray(X).reshape(-1,1)
        self._inner_ohc.fit(X, y)
        
    def fit_transform(self, X, y=None):
        X = np.asarray(X).reshape(-1,1)
        return self._inner_ohc.fit_transform(X, y)
    
    def transform(self, X):
        X = np.asarray(X).reshape(-1,1)
        return self._inner_ohc.transform(X)
    
    def inverse_transform(self, X):
        return self._inner_ohc.inverse_transform(X).reshape(-1)
    
    def get_feature_names_out(self, input_features=None):
        if input_features is not None:
            input_features = [input_features]
        return self._inner_ohc.get_feature_names_out(input_features)