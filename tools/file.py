import _pickle as pickle
from os import path, remove as file_del, rename as file_rename
from tools import log_tools

def pickle_objects(filename: str, a_list: list) -> None:
    json_path_old = filename[:-3] + 'old'
    json_path_old2 = json_path_old + '2'
    if path.isfile(filename):
        if path.isfile(json_path_old):
            if path.isfile(json_path_old2):
                file_del(json_path_old2)
            file_rename(json_path_old, json_path_old2)
        file_rename(filename, json_path_old)
    with open(filename, 'wb') as f:
        for i in a_list:
            pickle.dump(i, f, -1)
    log_tools.tprint(f'{filename} saved.')

def get_pickled_objects(filename) -> None:
    with open(filename, 'rb') as f:
        while 1:
            try:
                yield pickle.load(f)
            except EOFError:
                break
