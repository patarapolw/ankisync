import requests
from typing import Union


class AnkiConnect:
    URL = 'http://localhost:8765'
    VERSION = 6
    
    def __init__(self, version=6):
        self.VERSION = version

    def post(self, action, params: dict=None):
        j = {
            'action': action,
            'version': self.VERSION
        }
        if params:
            j['params'] = params
        r = requests.post(self.URL, json=j)
        resp = r.json()
        if resp['error']:
            raise ValueError(resp['error'])
        return resp['result']
    
    def version(self):
        return self.post('version')
    
    def upgrade(self):
        return self.post('upgrade')
    
    def sync(self):
        return self.post('sync')
    
    def multi(self, params):
        return self.post('multi', params=params)
    
    def deck_names(self):
        return self.post('deckNames')
    
    def deck_names_and_ids(self):
        return self.post('deckNamesAndIds')
    
    def get_decks(self, card_ids):
        return self.post('getDecks', params={
            'cards': card_ids
        })
    
    def create_deck(self, deck_name):
        return self.post('createDeck', params={
            'deck': deck_name
        })
    
    def change_deck(self, card_ids, deck_name):
        return self.post('changeDeck', params={
            'cards': card_ids,
            'deck': deck_name
        })
    
    def delete_decks(self, deck_names, cards_too: bool=False):
        return self.post('deleteDecks', params={
            'decks': deck_names,
            'cardsToo': cards_too
        })
    
    def get_deck_config(self, deck_name):
        return self.post('getDeckConfig', params={
            'deck': deck_name
        })
    
    def save_deck_config(self, config: dict):
        return self.post('saveDeckConfig', params={
            'config': config
        })
    
    def set_deck_config_id(self, deck_names, config_id):
        return self.post('setDeckConfigId', params={
            'decks': deck_names,
            'configId': config_id
        })
    
    def clone_deck_config_id(self, deck_name, clone_from: int):
        return self.post('cloneDeckConfigId', params={
            'deck': deck_name,
            'cloneFrom': clone_from
        })
    
    def remove_deck_config_id(self, config_id):
        return self.post('removeDeckConfigId', params={
            'configId': config_id
        })
    
    def model_names(self):
        return self.post('modelNames')
    
    def model_names_and_ids(self):
        return self.post('modelNamesAndIds')
    
    def model_field_names(self, model_name):
        return self.post('modelFieldNames', params={
            'modelName': model_name
        })
    
    def model_fields_on_templates(self, model_name):
        return self.post('modelFieldsOnTemplates', params={
            'modelName': model_name
        })
    
    def add_note(self, ac_note):
        return self.post('addNote', params={
            'note': ac_note
        })
    
    def add_notes(self, ac_notes):
        return self.post('addNotes', params={
            'notes': ac_notes
        })
    
    def can_add_notes(self, ac_notes):
        return self.post('canAddNotes', params={
            'notes': ac_notes
        })
    
    def update_note_fields(self, note_id, fields: dict):
        return self.post('updateNoteFields', params={
            'note': {
                'id': note_id,
                'fields': fields
            }
        })
    
    def add_tags(self, note_ids, tags: Union[str, list]):
        return self.post('addTags', params={
            'notes': note_ids,
            'tags': tags
        })
    
    def remove_tags(self, note_ids, tags: Union[str, list]):
        return self.post('removeTags', params={
            'notes': note_ids,
            'tags': tags
        })
    
    def get_tags(self):
        return self.post('getTags')
    
    def find_notes(self, query: str):
        return self.post('findNotes', params={
            'query': query
        })
    
    def notes_info(self, note_ids):
        return self.post('notesInfo', params={
            'notes': note_ids
        })
    
    def suspend(self, card_ids):
        return self.post('suspend', params={
            'cards': card_ids
        })
    
    def unsuspend(self, card_ids):
        return self.post('unsuspend', params={
            'cards': card_ids
        })
    
    def are_suspended(self, card_ids):
        return self.post('areSuspended', params={
            'cards': card_ids
        })
    
    def are_due(self, card_ids):
        return self.post('areDue', params={
            'cards': card_ids
        })
    
    def get_intervals(self, card_ids, complete=False):
        return self.post('getIntervals', params={
            'cards': card_ids,
            'complete': complete
        })
    
    def find_cards(self, query):
        return self.post('findCards', params={
            'query': query
        })
    
    def cards_to_notes(self, card_ids):
        return self.post('cardsToNotes', params={
            'cards': card_ids
        })
    
    def cards_info(self, card_ids):
        return self.post('cardsInfo', params={
            'cards': card_ids
        })
    
    def store_media_file(self, filename, data_b64):
        return self.post('storeMediaFile', params={
            'filename': filename,
            'data': data_b64
        })
    
    def retrieve_media_file(self, filename):
        return self.post('retrieveMediaFile', params={
            'filename': filename
        })
    
    def delete_media_file(self, filename):
        return self.post('deleteMediaFile', params={
            'filename': filename
        })
    
    def gui_browse(self, query):
        return self.post('guiBrowse', params={
            'query': query
        })
    
    def gui_add_cards(self):
        return self.post('guiAddCards')
    
    def gui_current_card(self):
        return self.post('guiCurrentCard')
    
    def gui_start_timer(self):
        return self.post('guiStartTimer')
    
    def gui_show_question(self):
        return self.post('guiShowQuestion')
    
    def gui_show_answer(self):
        return self.post('guiShowAnswer')
    
    def gui_answer_card(self, ease: int):
        return self.post('guiAnswerCard', params={
            'ease': ease
        })
    
    def gui_deck_overview(self, deck_name):
        return self.post('guiDeckOverview', params={
            'name': deck_name
        })
    
    def gui_deck_browser(self):
        return self.post('guiDeckBrowser')
    
    def gui_deck_review(self, deck_name):
        return self.post('guiDeckReview', params={
            'name': deck_name
        })
    
    def gui_exit_anki(self):
        return self.post('guiExitAnki')
