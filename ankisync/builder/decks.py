from time import time

from .default import default


class DeckBuilder(dict):
    """
    {
        name: "name of deck",
        extendRev: "extended review card limit (for custom study)",
        usn: "usn: Update sequence number: used in same way as other usn vales in db",
        collapsed: "true when deck is collapsed",
        browserCollapsed: "true when deck collapsed in browser",
        newToday: "two number. First one currently not used. Second is the negation (-)
                   of the number of new cards added today by custom study",
        timeToday: "two number array used somehow for custom study. Currently unused in the code",
        dyn: "1 if dynamic (AKA filtered) deck",
        extendNew: "extended new card limit (for custom study)",
        conf: "id of option group from dconf in `col` table",
        revToday: "two number. First one currently not used. Second is the negation (-)
                   of the number of review cards added today by custom study",
        lrnToday: "two number array used somehow for custom study. Currently unused in the code",
        id: "deck ID (automatically generated long)",
        mod: "last modification time",
        desc: "deck description"
    }
    """

    def __init__(self, name, desc='', dconf=1, id_=None, **kwargs):
        if id_ is None:
            self.id = int(time() * 1000)
        else:
            self.id = id_

        self.name = name
        d = next(iter(default['col']['decks'].values())).copy()
        d.update({
            "name": self.name,
            "id": self.id,
            "mod": int(time()),
            "desc": desc,
            "conf": dconf,
            **kwargs
        })

        super(DeckBuilder, self).__init__(d)


class DConfBuilder(dict):
    """
    {
    "model id (epoch time in milliseconds)" :
        {
            autoplay : "whether the audio associated to a question should be
    played when the question is shown"
            dyn : "Whether this deck is dynamic. Not present by default in decks.py"
            id : "deck ID (automatically generated long). Not present by default in decks.py"
            lapse : {
                "The configuration for lapse cards."
                delays : "The list of successive delay between the learning steps of the new cards, as explained in the manual."
                leechAction : "What to do to leech cards. 0 for suspend, 1 for mark. Numbers according to the order in which the choices appear in aqt/dconf.ui"
                leechFails : "the number of lapses authorized before doing leechAction."
                minInt: "a lower limit to the new interval after a leech"
                mult : "percent by which to multiply the current interval when a card goes has lapsed"
            }
            maxTaken : "The number of seconds after which to stop the timer"
            mod : "Last modification time"
            name : "The name of the configuration"
            new : {
                "The configuration for new cards."
                bury : "Whether to bury cards related to new cards answered"
                delays : "The list of successive delay between the learning steps of the new cards, as explained in the manual."
                initialFactor : "The initial ease factor"
                ints : "The list of delays according to the button pressed while leaving the learning mode. Good, easy and unused. In the GUI, the first two elements corresponds to Graduating Interval and Easy interval"
                order : "In which order new cards must be shown. NEW_CARDS_RANDOM = 0 and NEW_CARDS_DUE = 1."
                perDay : "Maximal number of new cards shown per day."
                separate : "Seems to be unused in the code."

            }
            replayq : "whether the audio associated to a question should be played when the answer is shown"
            rev : {
                "The configuration for review cards."
                bury : "Whether to bury cards related to new cards answered"
                ease4 : "the number to add to the easyness when the easy button is pressed"
                fuzz : "The new interval is multiplied by a random number between -fuzz and fuzz"
                ivlFct : "multiplication factor applied to the intervals Anki generates"
                maxIvl : "the maximal interval for review"
                minSpace : "not currently used according to decks.py code's comment"
                perDay : "Numbers of cards to review per day"
            }
            timer : "whether timer should be shown (1) or not (0)"
            usn : "See usn in cards table for details."
        }
    }
    """
    def __init__(self, name, **kwargs):
        self.name = name

        self.id = kwargs.setdefault('id', None)
        if self.id is None:
            self.id = int(time() * 1000)
        kwargs.pop('id')

        d = next(iter(default['col']['dconf'].values())).copy()
        d.update({
            "name": self.name,
            "id": self.id,
            **kwargs
        })

        super(DConfBuilder, self).__init__(d)
