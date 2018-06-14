import argparse
import json
import os
import pandas

import numpy as np

from scipy.sparse import coo_matrix, save_npz
from sklearn.model_selection import train_test_split

def get_args():
    #See also
    #https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_json.html
    #https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data',
        help = 'Location of the JSON/CSV file that contains input data.',
        required = True
        )
    parser.add_argument(
        '--output',
        help = 'Output directory that will store the test and training files. Defaults to current directory.',
        default = '.'
        )
    parser.add_argument(
        '--train-size',
        help = 'Proportion of the dataset that should be used for training. Default: 0.75',
        type = float,
        default = 0.75
        )
    parser.add_argument(
        '--k-cores',
        help = 'Remove items / users with fewer than k entries. Default: 5',
        type = int,
        default = 5
        )
    parser.add_argument(
        '--format',
        help = 'Format of the data file. For now, supports CSV and JSON. Default: csv',
        choices = ['csv', 'json'],
        type = str.lower,
        default = 'csv'
        )
    parser.add_argument(
        '--col-order',
        help = 'Ints or strings with the column indices / names of the columns with the user id, item id, and the rating. In that order. Default: 0 1 2',
        nargs = 3,
        default = [0, 1, 2]
        )
    parser.add_argument(
        '--save-map',
        help = 'Save the map from [0...nusers] to user ids and from [0...nitems] to item ids? Default: False.',
        type = bool,
        default = False
        )
    parser.add_argument(
        '--user-map',
        help = 'Name of the output file with the indices :-> user id map. Default: usermap.json',
        type = str,
        default = 'usermap.dat'
        )
    parser.add_argument(
        '--item-map',
        help = 'Name of the output file with the indices :-> item id map. Default: itemmap.json',
        type = str,
        default = 'itemmap.dat'
        )
    parser.add_argument(
        '--dtype',
        help = 'Datatype of the ratings. Default is 32 bit float.',
        choices = np.sctypeDict.keys(),
        type = np.dtype,
        default = np.float32
        )
    parser.add_argument(
        '--train-file',
        help = 'Name of the the output file containing the training matrix. Default: train.npz',
        default = 'train.npz'
        )
    parser.add_argument(
        '--test-file',
        help = 'Name of the the output file containing the training matrix. Default: test.npz',
        default = 'test.npz'
        )
    parser.add_argument(
        '--debug',
        help = 'Print extra debugging information.',
        type = bool,
        default = False
        )

    parsed, unknown = parser.parse_known_args()

    for arg in unknown:
        if arg.startswith(('-', '--')):
            parser.add_argument(arg)

    foward_args = {k : eval(v, {__builtins__ : None}, {}) for k, v in parser.parse_args().__dict__.items() if k not in parsed.__dict__}

    return parsed, foward_args

def handle_columns(array):
    try:
        return [int(x) for x in array], int
    except ValueError as _:
        return array, str

def json_dump(data, path):
    with open(path, 'w') as f:
        json.dump(data, f)

def get_map(array):
    return np.unique(array, return_inverse = True)

def k_filter(df, cols, k):
    _k_filter = lambda x : len(x) >= k 
    old_shape = df.shape
    df = df.groupby(cols[0]).filter(_k_filter)
    df = df.groupby(cols[1]).filter(_k_filter)
    if df.shape == old_shape:
        return df
    return k_filter(df, cols, k)

def main():
    args, kwargs = get_args()

    if args.format == 'csv':
        df = pandas.read_csv(args.data, **kwargs)
    elif args.format == 'json':
        df = pandas.read_json(args.data, **kwargs)

    cols, col_type = handle_columns(args.col_order)
    if col_type == int:
        cols = [df.columns[x] for x in cols]

    if args.k_cores > 0:
        df = k_filter(df, cols, args.k_cores)
    
    user_ids = df[cols[0]].values
    item_ids = df[cols[1]].values
    ratings = df[cols[2]].values.astype(np.int)

    user_map = get_map(user_ids)
    item_map = get_map(item_ids)
    
    if args.save_map:
        json_dump({k : v for v, k in enumerate(user_map[0])}, os.path.join(args.output, args.user_map))
        json_dump(item_map[0].tolist(), os.path.join(args.output, args.item_map))

    shape = (user_map[0].size, item_map[0].size)
    train_ratings, test_ratings, train_users, test_users, train_items, test_items = train_test_split(ratings, user_map[1], item_map[1], test_size = 1 - args.train_size)
    train = coo_matrix((train_ratings.astype(args.dtype), (train_users, train_items)), shape = shape)
    test = coo_matrix((test_ratings.astype(args.dtype), (test_users, test_items)), shape = shape)

    if args.debug:
        print('train: ', repr(train))
        print('test: ', repr(test))

    save_npz(os.path.join(args.output, args.train_file), train)
    save_npz(os.path.join(args.output, args.test_file), test)

if __name__ == '__main__':
    main()
