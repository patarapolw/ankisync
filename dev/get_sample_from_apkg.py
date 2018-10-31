from zipfile import ZipFile
from pathlib import Path

if __name__ == '__main__':
    with ZipFile('/Users/patarapolw/Google Drive/Zanki Physiology and Pathology.apkg') as zf:
        Path('sample').mkdir(exist_ok=True)
        zf.extractall('sample')
