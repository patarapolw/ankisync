import json
from importlib.resources import read_text

from ankisync.util import deep_merge_dicts

default = json.loads(read_text('ankisync.presets', 'default.json'))
wanki_min = json.loads(read_text('ankisync.presets', 'wanki_min.json'))
deep_merge_dicts(original=default, incoming=wanki_min)


def get_wanki_min_dconf():
    d = next(iter(wanki_min['col']['dconf'].values())).copy()

    return d
