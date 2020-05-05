from zipfile import ZipFile
from tempfile import mkdtemp
import atexit
import shutil
from pathlib import Path
import json

from .anki import Anki


class Apkg(Anki):
    def __init__(self, filename, **kwargs):
        self.filename = str(filename)
        self.temp_dir = mkdtemp()
        try:
            with ZipFile(self.filename) as zf:
                zf.extractall(path=self.temp_dir)

            self.media = json.loads(Path(self.temp_dir).joinpath('media').read_text())
        except FileNotFoundError:
            self.media = dict()

        atexit.register(shutil.rmtree, self.temp_dir, ignore_errors=True)

        super(Apkg, self).__init__(str(Path(self.temp_dir).joinpath('collection.anki2')), **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.save()
        shutil.rmtree(self.temp_dir)

    def save(self):
        with ZipFile(self.filename, 'w') as zf:
            zf.write(str(Path(self.temp_dir).joinpath('collection.anki2')), arcname='collection.anki2')
            for file_path in Path(self.temp_dir).glob('*'):
                if str(Path(file_path).name).isdigit():
                    zf.write(Path(self.temp_dir).joinpath(file_path).resolve(), arcname=file_path.name)

            zf.writestr('media', json.dumps(self.media))

    def store_media_file(self, filename, data_binary):
        if len(self.media.keys()) == 0:
            media_id = 1
        else:
            media_id = max(int(k) for k in self.media.keys()) + 1

        with Path(self.temp_dir).joinpath(str(media_id)).open('wb') as f:
            f.write(data_binary)

        self.media[str(media_id)] = filename

    def retrieve_media_file(self, filename):
        for k, v in self.media.items():
            if v == filename:
                return Path(self.temp_dir).joinpath(k).read_bytes()

    def delete_media_file(self, filename):
        for k, v in self.media.items():
            if v == filename:
                self.media.pop(k)
                return True

        return False
