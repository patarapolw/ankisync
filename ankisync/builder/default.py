from ankisync.presets import default


def create_conf(**kwargs):
    d = default.copy()['conf']
    d.update(kwargs)

    return d


def create_tags():
    return default.copy()['tags']
