import sqlite3
import json
# import oyaml
from collections import OrderedDict

from ankisync.dir import get_collection_path


def sample_anki2(filename=None):
    if filename is None:
        filename = get_collection_path()

    d = OrderedDict()

    conn = sqlite3.connect(filename)
    conn.row_factory = sqlite3.Row

    table_names = [c[0] for c in conn.execute("SELECT name FROM sqlite_master WHERE type='table';")]
    for table_name in table_names:
        r = conn.execute(f'SELECT * FROM "{table_name}"').fetchone()
        if r is not None:
            if table_name == 'col':
                for k in r.keys():
                    v = r[k]
                    try:
                        v = json.loads(v)
                    except (TypeError, json.decoder.JSONDecodeError):
                        pass

                    d.setdefault(table_name, OrderedDict())[k] = v
            else:
                d[table_name] = OrderedDict(r)
        else:
            d[table_name] = None

    return d


if __name__ == '__main__':
    with open('sample.json', 'w') as f:
        json.dump(sample_anki2(), f, indent=2)
