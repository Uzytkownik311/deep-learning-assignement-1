from .dataset import Dataset
from .ops import Op

import typing
import numpy as np
import random

class Batch:
    '''
    A (mini)batch generated by the batch generator.
    '''

    def __init__(self):

        '''
        Ctor.
        '''

        self.data = None
        self.label = None
        self.idx = None

class BatchGenerator:
    '''
    Batch generator.
    Returned batches have the following properties:
      data: numpy array holding batch data of shape (s, SHAPE_OF_DATASET_SAMPLES).
      labels: numpy array holding batch labels of shape (s, SHAPE_OF_DATASET_LABELS).
      idx: numpy array with shape (s,) encoding the indices of each sample in the original dataset.
    '''

    def __init__(self, dataset: Dataset, num: int, shuffle: bool, op: Op = None):
        '''
        Ctor.
        Dataset is the dataset to iterate over.
        num is the number of samples per batch. the number in the last batch might be smaller than that.
        shuffle controls whether the sample order should be preserved or not.
        op is an operation to apply to input samples.
        Raises TypeError on invalid argument types.
        Raises ValueError on invalid argument values, such as if num is > len(dataset).
        '''

        self._batches = []
        dataset_size = len(dataset)

        if not isinstance(dataset, Dataset):
            raise TypeError("The argument dataset is not instance of class Dataset.")

        if not np.issubdtype(type(num), np.integer):
            raise TypeError("The batch size is not integer type, but: " + str(type(num)) + ".")

        if num > dataset_size:
            raise ValueError("The number os samples per batch should be smaller then dataset size,"
                             "database size is: " + str(dataset_size) + " batch size is: " + str(num) + ".")

        if num < 1:
            raise ValueError("The number os samples per batch should be grater then 1, it is: " + str(num) + ".")

        if shuffle:
            dataset = list(dataset)
            random.shuffle(dataset)

        label = np.empty((dataset_size,), int)
        label[0] = dataset[0].label
        idx = np.empty((dataset_size,), int)
        idx[0] = dataset[0].idx

        if not op:
            data_shape = (dataset_size, ) + dataset[0].data.shape
            data = np.empty(data_shape)
            data[0] = dataset[0].data
        else:
            tmp_data = op(dataset[0].data)
            data_shape = (dataset_size,) + tmp_data.shape
            data = np.empty(data_shape, tmp_data.dtype)
            data[0] = tmp_data

        for i in range(1, dataset_size):
            label[i] = dataset[i].label
            idx[i] = dataset[i].idx
            if not op:
                data[i] = dataset[i].data
            else:
                data[i] = op(dataset[i].data)

        for i in range(0, dataset_size, num):
            if i+num <= dataset_size:
                batch_offset = i+num
            else:
                batch_offset = dataset_size
            batch = Batch()
            batch.data = data[i:batch_offset]
            batch.label = label[i:batch_offset]
            batch.idx = idx[i:batch_offset]
            self._batches.append(batch)


    def __len__(self) -> int:
        '''
        Returns the number of batches generated per iteration.
        '''

        return len(self._batches)

    def __iter__(self) -> typing.Iterable[Batch]:
        '''
        Iterate over the wrapped dataset, returning the data as batches.
        '''

        for i in self._batches:
            yield i

