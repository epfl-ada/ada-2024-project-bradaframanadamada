#import torch
#import numpy as np
#from torch.utils.data import Dataset
import pandas as pd

"""
class SomeDataset(Dataset):
    \"\"\"
    A dataset implements 2 functions
        - __len__  (returns the number of samples in our dataset)
        - __getitem__ (returns a sample from the dataset at the given index idx)
    \"\"\"

    def __init__(self, dataset_parameters, **kwargs):
        super().__init__()

    def __getitem__(self, index):


class SomeDatamodule(DataLoader):
     \"\"\"
    Allows you to sample train/val/test data, to later do training with models.
        
    \"\"\"
    def __init__(self):
        super().__init__()
"""


def load_tsv(path: str, header=None) -> pd.DataFrame:
    """
        Loads a tsv file and store it in a Pandas Dataframe

        :param path: Path to data tsv file
        :param header: id of rows to consider as header
        :return: A Pandas Dataframe containing the data
    """
    df = pd.read_csv(path, sep='\t', header=header)
    return df
