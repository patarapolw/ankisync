from typing import Union
import warnings
import psutil
from time import time

from . import db
from .dir import get_collection_path
from .builder.models import ModelBuilder
from .builder.decks import DeckBuilder, DConfBuilder
from .builder.notes import NoteBuilder, CardBuilder


class Anki:
    def __init__(self, anki2_path=None, disallow_unsafe: Union[bool, None]=False, **kwargs):
        if anki2_path is None:
            anki2_path = get_collection_path(account_name=kwargs.setdefault('account_name', None))
            try:
                assert 'Anki' not in (p.name() for p in psutil.process_iter()), \
                    "Please close Anki first before accessing Application Data collection.anki2 directly."
            except psutil.ZombieProcess as e:
                warnings.warn(e)
            kwargs.pop('account_name')

        db.database.init(anki2_path, pragmas={
            'foreign_keys': 0
        }, **kwargs)

        self.disallow_unsafe = disallow_unsafe

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _warning(self):
        msg = 'Please use _id() methods instead.'

        if self.disallow_unsafe is True:
            raise ValueError(msg)
        elif self.disallow_unsafe is False:
            warnings.warn(msg)
        else:
            pass


    @classmethod
    def init(cls,
             first_model: ModelBuilder,
             first_deck: DeckBuilder,
             first_dconf: DConfBuilder=None,
             first_note_data=None):
        db.database.create_tables([db.Col, db.Notes, db.Cards, db.Revlog, db.Graves])

        db_models = dict()
        db_models[str(first_model.id)] = first_model

        db_decks = dict()
        db_decks[str(first_deck.id)] = first_deck

        if first_dconf is None:
            first_dconf = DConfBuilder('Default')

        db_dconf = dict()
        db_dconf[str(first_dconf.id)] = first_dconf

        if not db.Col.get_or_none():
            db.Col.create(
                models=db_models,
                decks=db_decks,
                dconf=db_dconf
            )

        if not db.Notes.get_or_none():
            if first_note_data is None:
                first_note_data = dict()
            first_note = NoteBuilder(model_id=first_model.id,
                                     model_field_names=first_model.field_names,
                                     data=first_note_data)
            db_notes = db.Notes.create(**first_note)
            first_note.id = db_notes.id

            for template_name in first_model.template_names:
                first_card = CardBuilder(first_note, first_deck.id, template_name)
                db.Cards.create(**first_card)

    @classmethod
    def add_model(cls, name, fields, templates, **kwargs):
        db_col = db.Col.get()
        db_models = db_col.models
        new_model = ModelBuilder(name, fields, templates, **kwargs)
        db_models[str(new_model.id)] = new_model
        db_col.models = db_models
        db_col.save()

        return new_model.id

    @classmethod
    def change_deck_by_id(cls, card_ids, deck_id)->None:
        db.Cards.update(did=deck_id).where(db.Cards.id.in_(card_ids)).execute()

    @classmethod
    def delete_decks_by_id(cls, deck_ids, cards_too=False)->None:
        db_col = db.Col.get()
        db_decks = db_col.decks

        for deck_id in deck_ids:
            db_decks.pop(str(deck_id))
            if cards_too:
                for db_card in db.Cards.select().where(db.Cards.did == int(deck_id)):
                    db_card.delete_instance()

        db_col.decks = db_decks
        db_col.save()

    @classmethod
    def model_by_id(cls, model_id):
        return db.Col.get().models[str(model_id)]

    @classmethod
    def model_field_names_by_id(cls, model_id):
        model = cls.model_by_id(model_id)
        return [f['name'] for f in model['flds']]

    @classmethod
    def model_template_names_by_id(cls, model_id):
        model = cls.model_by_id(model_id)
        return [t['name'] for t in model['tmpls']]

    @classmethod
    def note_to_cards(cls, note_id):
        def _get_dict():
            db_note = db.Notes.get(id=note_id)
            template_names = cls.model_template_names_by_id(db_note.mid)

            for c in db.Cards.select(db.Cards.id, db.Cards.ord, db.Cards.nid).where(db.Cards.nid == note_id):
                yield template_names[c.ord], c.id

        return dict(_get_dict())

    @classmethod
    def card_set_next_review(cls, card_id, type, queue, due):
        """

        :param card_id:
        :param type:
        -- 0=new, 1=learning, 2=due, 3=filtered
        :param queue:
        -- -3=sched buried, -2=user buried, -1=suspended,
        -- 0=new, 1=learning, 2=due (as for type)
        -- 3=in learning, next rev in at least a day after the previous review
        :param due:
        -- Due is used differently for different card types:
        --   new: note id or random int
        --   due: integer day, relative to the collection's creation time
        --   learning: integer timestamp
        :return:
        """
        db_card = db.Cards.get(id=card_id)
        db_card.type = type
        db_card.queue = queue
        db_card.due = due
        db_card.save()

    @classmethod
    def card_set_stat(cls, card_id, reps, lapses, **revlog):
        """

        :param card_id:
        :param reps:
        -- number of reviews
        :param lapses:
        -- the number of times the card went from a "was answered correctly"
        --   to "was answered incorrectly" state
        :param revlog:
        usn             integer not null,
            -- update sequence number: for finding diffs when syncing.
            --   See the description in the cards table for more info
        ease            integer not null,
           -- which button you pushed to score your recall.
           -- review:  1(wrong), 2(hard), 3(ok), 4(easy)
           -- learn/relearn:   1(wrong), 2(ok), 3(easy)
        ivl             integer not null,
           -- interval
        lastIvl         integer not null,
           -- last interval
        factor          integer not null,
          -- factor
        time            integer not null,
           -- how many milliseconds your review took, up to 60000 (60s)
        type            integer not null
           --  0=learn, 1=review, 2=relearn, 3=cram
        :return:
        """
        with db.database.atomic():
            db_card = db.Cards.get(id=card_id)
            db_card.reps = reps
            db_card.lapses = lapses
            db_card.save()

            db.Revlog.create(
                cid=db_card.id,
                **revlog
            )

    @classmethod
    def get_deck_config_by_deck_name(cls, deck_name):
        deck_id = cls.deck_names_and_ids()[deck_name]
        conf_id = db.Col.get().decks[str(deck_id)]['conf']
        db_dconf = db.Col.get().dconf

        return db_dconf[str(conf_id)]

    @classmethod
    def deck_config_names_and_ids(cls):
        def _gen_dict():
            for dconf_id, d in db.Col.get().dconf.items():
                yield d['name'], int(dconf_id)

        return dict(_gen_dict())

    ################################
    # Original AnkiConnect Methods #
    ################################

    @classmethod
    def deck_names(cls):
        return [d['name'] for d in db.Col.get().decks.values()]

    @classmethod
    def deck_names_and_ids(cls):
        def _gen_dict():
            for did, d in db.Col.get().decks.items():
                yield d['name'], int(did)

        return dict(_gen_dict())

    @classmethod
    def get_decks(cls, card_ids):
        def _gen_dict():
            for did, d in db.Col.get().decks.items():
                db_cards = db.Cards.select(db.Cards.id, db.Cards.did)\
                    .where((db.Cards.did == int(did)) & (db.Cards.id.in_(card_ids)))
                if len(db_cards) > 0:
                    yield d['name'], [c.id for c in db_cards]

        return dict(_gen_dict())

    @classmethod
    def create_deck(cls, deck_name, desc='', dconf=1, **kwargs):
        db_col = db.Col.get()
        db_decks = db_col.decks
        existing_decks = cls.deck_names()

        deck_name_parts = deck_name.split('::')
        sub_deck_parts = []
        for i, part in enumerate(deck_name_parts):
            sub_deck_parts.append(part)
            sub_deck = '::'.join(sub_deck_parts)
            if sub_deck not in existing_decks:
                new_deck = DeckBuilder(name=sub_deck, desc=desc, dconf=dconf, id_=int(time() * 1000) + i, **kwargs)
                db_decks[str(new_deck.id)] = new_deck

        db_col.decks = db_decks
        db_col.save()

        return cls.deck_names_and_ids()[deck_name]

    def change_deck(self, card_ids, deck_name, dconf=1):
        self._warning()

        deck_id = self.deck_names_and_ids().get(deck_name, None)
        if deck_id is None:
            deck_id = self.create_deck(deck_name, dconf=dconf)

        self.change_deck_by_id(card_ids, deck_id)

    def delete_decks(self, deck_names, cards_too=False):
        self._warning()

        deck_mapping = self.deck_names_and_ids()
        deck_ids = [deck_mapping[deck_name] for deck_name in deck_names]

        self.delete_decks_by_id(deck_ids, cards_too)

    def get_deck_config(self, deck_name):
        self._warning()

        return self.get_deck_config_by_deck_name(deck_name)

    @classmethod
    def save_deck_config(cls, config: dict):
        db_col = db.Col.get()
        db_dconf = db_col.dconf

        dconf = DConfBuilder(config.pop('name'), **config)
        db_dconf[str(dconf.id)] = dconf

        db_col.dconf = db_dconf
        db_col.save()

        return dconf.id

    @classmethod
    def set_deck_config_id(cls, deck_names, config_id):
        is_edited = False
        db_col = db.Col.get()
        db_decks = db_col.decks

        for k, v in cls.deck_names_and_ids().items():
            if k in deck_names:
                db_decks[str(v)]['conf'] = config_id
                is_edited = True

        if is_edited:
            db_col.decks = db_decks
            db_col.save()

        return is_edited

    @classmethod
    def clone_deck_config_id(cls, dconf_name, clone_from: int):
        db_col = db.Col.get()
        db_dconf = db_col.dconf
        new_dconf = DConfBuilder(dconf_name)
        new_dconf.update(db_dconf[str(clone_from)])
        db_dconf[new_dconf.id] = new_dconf
        db_col.dconf = db_dconf
        db_col.save()

        return new_dconf.id

    @classmethod
    def remove_deck_config_id(cls, config_id):
        db_col = db.Col.get()
        db_dconf = db_col.dconf
        db_dconf.pop(config_id)
        db_col.dconf = db_dconf
        db_col.save()

        return True

    @classmethod
    def model_names(cls):
        return [m['name'] for m in db.Col.get().models.values()]

    @classmethod
    def model_names_and_ids(cls):
        def _gen_dict():
            for mid, m in db.Col.get().models.items():
                yield m['name'], int(mid)

        return dict(_gen_dict())

    @classmethod
    def model_field_names(cls, model_name):
        model_id = cls.model_names_and_ids()[model_name]
        return cls.model_field_names_by_id(model_id)

    @classmethod
    def model_template_names(cls, model_name):
        model_id = cls.model_names_and_ids()[model_name]
        return cls.model_template_names_by_id(model_id)

    # @classmethod
    # def model_fields_on_templates(cls, model_name):
    #     raise NotImplementedError

    def add_note(self, ac_note):
        deck_id = ac_note.get('deckId', None)
        if deck_id is None:
            self._warning()

            deck_name = ac_note['deckName']
            deck_id = self.deck_names_and_ids().get(deck_name, None)

            if deck_id is None:
                deck_id = self.create_deck(deck_name, conf=ac_note.get('dconf', 1))

        model_id = ac_note.get('modelId', None)
        if model_id is None:
            self._warning()

            model_name = ac_note['modelName']
            model_id = self.model_names_and_ids()[model_name]

        data = ac_note['fields']
        tags = ac_note.get('tags', [])

        model_field_names = self.model_field_names_by_id(model_id)

        first_note = NoteBuilder(model_id=model_id,
                                 model_field_names=model_field_names,
                                 data=data,
                                 tags=tags)
        db_notes = db.Notes.create(**first_note)
        first_note.id = db_notes.id

        for i, template_name in enumerate(self.model_template_names_by_id(model_id)):
            first_card = CardBuilder(first_note, deck_id, template=i)
            db.Cards.create(**first_card)

        return db_notes.id

    def add_notes(self, ac_notes):
        return [self.add_note(ac_note) for ac_note in ac_notes]

    # @classmethod
    # def can_add_notes(cls, ac_notes):
    #     raise NotImplementedError

    @classmethod
    def update_note_fields(cls, note_id, fields: dict):
        db_note = db.Notes.get(id=note_id)
        field_names = cls.model_field_names_by_id(db_note.mid)
        prev_note_fields = db_note.flds
        note_fields = []
        for i, name in enumerate(field_names):
            note_field = fields.get(name, None)
            if note_field is not None:
                note_fields.append(note_field)
            else:
                note_fields.append(prev_note_fields[i])

        db_note.flds = note_fields
        db_note.save()

    @classmethod
    def add_tags(cls, note_ids, tags: Union[str, list]):
        if isinstance(tags, str):
            tags = [tags]

        db.Notes.update(
            tags=sorted(set(db.Notes.tags) | set(tags))
        ).where(db.Notes.id.in_(note_ids))

    @classmethod
    def remove_tags(cls, note_ids, tags: Union[str, list]):
        if isinstance(tags, str):
            tags = [tags]

        db.Notes.update(
            tags=sorted(set(db.Notes.tags) - set(tags))
        ).where(db.Notes.id.in_(note_ids))

    @classmethod
    def get_tags(cls):
        all_tags = set()
        for db_note in db.Notes.select(db.Notes.tags):
            all_tags.update(db_note.tags)

        return sorted(all_tags)

    # @classmethod
    # def find_notes(cls, query: str):
    #     raise NotImplementedError

    @classmethod
    def notes_info(cls, note_ids):
        all_info = list()
        for db_note in db.Notes.select().where(db.Notes.id.in_(note_ids)):
            db_model = cls.model_by_id(db_note.mid)
            all_info.append({
                'noteId': db_note.id,
                'modelId': db_note.mid,
                'tags': db_note.tags,
                'fields': dict(zip(db_model['flds'], db_note.flds))
            })

        return all_info

    @classmethod
    def suspend(cls, card_ids):
        if db.Cards.update(queue=-1).where(db.Cards.id.in_(card_ids)).execute() > 0:
            return True

        return False

    @classmethod
    def unsuspend(cls, card_ids):
        if db.Cards.update(queue=db.Cards.type).where(db.Cards.id.in_(card_ids)).execute() > 0:
            return True

        return False

    @classmethod
    def are_suspended(cls, card_ids):
        def _gen_list():
            for card_id in card_ids:
                db_card = db.Cards.get(id=card_id)
                yield (db_card.queue == -1)

        return list(_gen_list())

    @classmethod
    def are_due(cls, card_ids):
        def _gen_list():
            for card_id in card_ids:
                db_card = db.Cards.get(id=card_id)
                yield (db_card.type == 2)

        return list(_gen_list())

    # @classmethod
    # def get_intervals(cls, card_ids, complete=False):
    #     raise NotImplementedError
    #
    # @classmethod
    # def find_cards(cls, query):
    #     raise NotImplementedError

    @classmethod
    def cards_to_notes(cls, card_ids):
        note_ids = set()
        for db_card in db.Cards.select(db.Cards.id, db.Cards.nid).where(db.Cards.id.in_(card_ids)):
            note_ids.update(db_card.nid)

        return sorted(note_ids)

    @classmethod
    def cards_info(cls, card_ids):
        all_info = list()
        for card_id in card_ids:
            db_card = db.Cards.get(id=card_id)
            all_info += cls.notes_info([db_card.nid])

        return all_info
