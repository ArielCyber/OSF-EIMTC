import pathlib
import os

class FilenameBasedLabelling:
    '''
    General Purpose
    '''
    def __init__(self, label_name='eimtc_default_label1'):
        self.label_name = label_name

    def __call__(self, filepath):
        label = get_filename(filepath)
        return {self.label_name: label}


class DirectoryBasedLabelling:
    '''
    General Purpose
    '''
    def __init__(self, root=None, label_names=None):
        self.root = root
        self.label_names = label_names

    def __call__(self, filepath):
        if self.label_names is None:
            label_names = iter(label_name_generator())
        else:
            label_names = iter(self.label_names)
            
        labels = []
        for p in pathlib.Path(filepath).relative_to(self.root).parents:
            label = p.name
            if label != '':
                labels.append(label)
                
        return dict(
            zip(
                label_names, 
                reversed(labels)
            )
        )


def get_filename(filepath):
    '''
    General Purpose
    '''
    return pathlib.Path(filepath).stem


def label_name_generator():
    last_num = 1
    while True:
        yield 'eimtc_default_label'+str(last_num)
        last_num += 1
