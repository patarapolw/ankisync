import os

from ankisync.dir import get_collection_path

if __name__ == '__main__':
    os.unlink(get_collection_path())
