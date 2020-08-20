import os

import appdirs


def get_collection_path(account_name: str=None):
    app_dir = appdirs.user_data_dir('Anki2', appauthor=False, roaming=True)

    if account_name is None:
        account_name = 'User 1'

    return os.path.join(app_dir, account_name)

app_dir = get_collection_path()
print(app_dir)
print(os.listdir(app_dir))