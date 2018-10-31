# ankisync

Doing what AnkiConnect cannot do, including
- Creating new `*.apkg`
- Creating new note type / model
- Setting next review
- Setting card statistics
- Note ids to Card ids

## Usage

Please close your `Anki` application first before doing this!

```python
from ankisync.anki import Anki
from ankisync.builder import FieldBuilder, TemplateBuilder
with Anki() as a:
    a.add_model(
        name='foo',
        fields=[FieldBuilder(name, i).get() for i, name in enumerate(['field_a', 'field_b', 'field_c'])],
        templates=[TemplateBuilder(
            name=k,
            question=q,
            answer=a,
            order=i
        ).get() for i, (k, [q,a]) in enumerate({
            'Forward': [QUESTION1, ANSWER1],
            'Reverse': [QUESTION2, ANSWER2]
        }.items())]
    )
```

Most of the other API's are similar to AnkiConnect, but `_by_id()`'s are preferred.

Creating a new `*.apkg` is also possible.

```python
from ankisync.apkg import Apkg
from ankisync.builder import FieldBuilder, TemplateBuilder, ModelBuilder, DeckBuilder
with Apkg('bar.apkg') as a:
    model_id = a.init(
        first_model=ModelBuilder(
            name='foo',
            fields=[FieldBuilder(name, i).get() for i, name in enumerate(['field_a', 'field_b', 'field_c'])],
            templates=[TemplateBuilder(
                name=k,
                question=q,
                answer=a,
                order=i
            ).get() for i, (k, [q,a]) in enumerate({
                'Forward': [QUESTION1, ANSWER1],
                'Reverse': [QUESTION2, ANSWER2]
            }.items())]
        ),
        first_deck=DeckBuilder(name='baz')
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

For the example of how I use it in action, see https://github.com/patarapolw/zhlib/blob/09aa27157e6876398aa14f12b2917bd9dafee959/zhlib/export.py#L56

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
