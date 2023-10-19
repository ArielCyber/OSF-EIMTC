import unittest
import numpy as np
from numpy.testing import assert_array_equal
from EIMTC.preprocessing import OneHotEncoderEIMTC, FilenameBasedLabelling, DirectoryBasedLabelling


class TestFilenameBasedLabelling(unittest.TestCase):

    def test_filename_based_labelling1(self):
        # Given
        filepath = r'D:/dir1/dir2/filename1.pcap'
        label_name = 'lbl_name1'
        method = FilenameBasedLabelling(label_name)
        # When
        res = method(filepath)
        # Then
        self.assertEqual(res, {'lbl_name1': 'filename1'})
        
    def test_filename_based_labelling2(self):
        # Given
        filepath = r'D:/dir1/dir2/somethingNAME.pcap'
        label_name = 'lbl_name1'
        method = FilenameBasedLabelling(label_name)
        # When
        res = method(filepath)
        # Then
        self.assertEqual(res, {'lbl_name1': 'somethingNAME'})



class TestDirectoryBasedLabelling(unittest.TestCase):

    def test_directory_based_labelling_single(self):
        # Given
        filepath = r'D:/dir1/lbldir1/filename1.pcap'
        root = r'D:/dir1/'
        label_names = ['lbl_name1']
        method = DirectoryBasedLabelling(root, label_names)
        # When
        res = method(filepath)
        # Then
        self.assertEqual(res, {'lbl_name1': 'lbldir1'})
        
    def test_directory_based_labelling_2_layers_deep(self):
        # Given
        filepath = r'D:/dir1/lbldir1/lbldir2/filename1.pcap'
        root = r'D:/dir1/'
        label_names = ['lbl_name1', 'lbl_name2']
        method = DirectoryBasedLabelling(root, label_names)
        # When
        res = method(filepath)
        # Then
        self.assertEqual(res, {
            'lbl_name1': 'lbldir1',
            'lbl_name2': 'lbldir2'
        })



class TestOneHotEncoderEIMTC(unittest.TestCase):

    def test_onehotencoder_categories(self):
        # Given
        enc = OneHotEncoderEIMTC(sparse=False)
        X = sorted(['Male', 'Female', 'Other'])
        enc.fit(X)
        # When
        res = enc.categories_
        # Then
        assert_array_equal(res, X)
        
    def test_onehotencoder_fit_transform(self):
        # Given
        enc = OneHotEncoderEIMTC(sparse=False)
        X = sorted(['Male', 'Female', 'Other'])
        # When
        res = enc.fit_transform(X)
        # Then
        assert_array_equal(res, np.array([
            [1,0,0],
            [0,1,0],
            [0,0,1],
        ]))
        
    def test_onehotencoder_fit_transform_multiple_samples(self):
        # Given
        enc = OneHotEncoderEIMTC(sparse=False)
        X = ['Male', 'Male', 'Other', 'Female', 'Other']
        # When
        res = enc.fit_transform(X)
        # Then
        assert_array_equal(res, np.array([
            [0,1,0],
            [0,1,0],
            [0,0,1],
            [1,0,0],
            [0,0,1],
        ]))


    def test_onehotencoder_fit_and_then_transform_multiple_samples(self):
        # Given
        enc = OneHotEncoderEIMTC(sparse=False)
        X = ['Male', 'Male', 'Other', 'Female', 'Other']
        X2 = ['Male', 'Other', 'Male']
        enc.fit(X)
        # When
        res = enc.transform(X2)
        # Then
        assert_array_equal(res, np.array([
            [0,1,0],
            [0,0,1],
            [0,1,0],
        ]))
        
    def test_onehotencoder_inverse_transform(self):
        # Given
        enc = OneHotEncoderEIMTC(sparse=False)
        X = ['Male', 'Male', 'Other', 'Female', 'Other']
        transformed = [
            [0,1,0],
            [0,0,1],
            [0,1,0]
        ]
        enc.fit(X)
        # When
        res = enc.inverse_transform(transformed)
        # Then
        assert_array_equal(res, ['Male', 'Other', 'Male'])