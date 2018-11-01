# ankisync

[![PyPI version shields.io](https://img.shields.io/pypi/v/ankisync.svg)](https://pypi.python.org/pypi/ankisync/)
[![PyPI license](https://img.shields.io/pypi/l/ankisync.svg)](https://pypi.python.org/pypi/ankisync/)

Doing what AnkiConnect cannot do, including
- Creating new `*.apkg`
- Creating new note type / model
- Upserting notes
- Setting next review
- Setting card statistics
- Note ids to Card ids

But of course, this is very unsafe compared to pure AnkiConnect. I will not hold liability to damage it may cost.

## Usage

Please close your `Anki` application first before doing this!

```python
from ankisync.anki import Anki
with Anki() as a:
    a.add_model(
        name='foo',
        fields=['field_a', 'field_b', 'field_c'],
        templates={
            'Forward': (QUESTION1, ANSWER1),
            'Reverse': (QUESTION2, ANSWER2)
        }
    )
```

Most of the other API's are similar to AnkiConnect, but `_by_id()`'s are preferred.

Creating a new `*.apkg` is also possible.

```python
from ankisync.apkg import Apkg
with Apkg('bar.apkg') as a:
    model_id = a.init(
        first_model=dict(
            name='foo',
            fields=['field_a', 'field_b', 'field_c'],
            templates={
                'Forward': (QUESTION1, ANSWER1),
                'Reverse': (QUESTION2, ANSWER2)
            }
        ),
        first_deck='baz'
    )
    a.add_note({
        'modelName': 'foo',
        'deckId': 1,  # "Default" deck
        'fields': {
            'field_a': 'aaaaa',
            'field_b': 123  # Numbers will be converted to string.
        }
    })
```

For the example of how I use it in action, see https://github.com/patarapolw/zhlib/blob/master/zhlib/export.py

## Installation

```
pip install ankisync
```

## Contributions

- What features outside AnkiConnect (or inside) do you want? I will try to implement it.
- Help me understand the documentations, [AnkiDroid Wiki](https://github.com/ankidroid/Anki-Android/wiki/Database-Structure), and [Anki decks collaboration Wiki](http://decks.wikia.com/wiki/Anki_APKG_format_documentation) 
- Please help me implement the `NotImplemented` methods.

## Note

- This is the successor to [AnkiTools](https://github.com/patarapolw/AnkiTools). I will not update it anymore.
