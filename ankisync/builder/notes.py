from typing import Union

from .models import ModelBuilder


class NoteBuilder(dict):
    def __init__(self, model_id, model_field_names, data: dict, tags=None, note_id=None, **kwargs):
        self.model_id = model_id
        self.model_field_names = model_field_names
        self.data = data
        self.id = note_id

        if tags:
            self.tags = tags
        else:
            self.tags = list()

        super(NoteBuilder, self).__init__(
            mid=self.model_id,
            tags=self.tags,
            **kwargs
        )
        flds = []
        for field_name in self.model_field_names:
            flds.append(str(self.data.get(field_name, '')))
        self['flds'] = flds


class CardBuilder(dict):
    def __init__(self,
                 note: Union[NoteBuilder, int],
                 deck_id: int,
                 template: Union[int, str],
                 model: ModelBuilder=None,
                 **kwargs):
        self.note = note
        self.deck_id = deck_id
        self.template = template
        self.model = model

        super(CardBuilder, self).__init__(
            nid=getattr(self.note, 'id', self.note),
            did=self.deck_id,
            **kwargs
        )
        if isinstance(self.template, int):
            self['ord'] = self.template
        else:
            self['ord'] = self.model.template_names.index(self.template)
