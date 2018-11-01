from time import time

from .default import default


class ModelBuilder(dict):
    """
    {
    "model id (epoch time in milliseconds)" :
      {
        css : "CSS, shared for all templates",
        did :
            "Long specifying the id of the deck that cards are added to by default",
        flds : [
                 "JSONArray containing object for each field in the model as follows:",
                 {
                   font : "display font",
                   media : "array of media. appears to be unused",
                   name : "field name",
                   ord : "ordinal of the field - goes from 0 to num fields -1",
                   rtl : "boolean, right-to-left script",
                   size : "font size",
                   sticky : "sticky fields retain the value that was last added
                               when adding new notes"
                 }
               ],
        id : "model ID, matches notes.mid",
        latexPost : "String added to end of LaTeX expressions (usually \\end{document})",
        latexPre : "preamble for LaTeX expressions",
        mod : "modification time in milliseconds",
        name : "model name",
        req : [
                "Array of arrays describing which fields are required
                    for each card to be generated, looks like: [[0, "any", [0, 3, 6]]], this is required to display a template",
                [
                  "the 'ord' value of the template object from the 'tmpls' array you are setting the required fields of",
                  '? string, "all" or "any"',
                  ["? another array of 'ord' values from field object you want to require from the 'flds' array"]
                ]
              ],
        sortf : "Integer specifying which field is used for sorting in the browser",
        tags : "Anki saves the tags of the last added note to the current model, use an empty array []",
        tmpls : [
                  "JSONArray containing object of CardTemplate for each card in model",
                  {
                    afmt : "answer template string",
                    bafmt : "browser answer format:
                              used for displaying answer in browser",
                    bqfmt : "browser question format:
                              used for displaying question in browser",
                    did : "deck override (null by default)",
                    name : "template name",
                    ord : "template number, see flds",
                    qfmt : "question format string"
                  }
                ],
        type : "Integer specifying what type of model. 0 for standard, 1 for cloze",
        usn : "usn: Update sequence number: used in same way as other usn vales in db",
        vers : "Legacy version number (unused), use an empty array []"
      }
    }
    """
    def __init__(self, name, fields, templates, type_=0, **kwargs):
        if isinstance(fields[0], str):
            fields = [FieldBuilder(
                name=name,
                order=i
            ) for i, name in enumerate(fields)]

        if isinstance(templates, dict):
            templates = [TemplateBuilder(
                name=k,
                question=q,
                answer=a,
                order=i
            ) for i, (k, (q, a)) in enumerate(templates.items())]

        self.id = int(time() * 1000)
        self.name = name
        self.fields = fields
        self.templates = templates
        req = [[i, "all", [i]] for i in range(len(self.templates))]

        d = next(iter(default['col']['models'].values())).copy()
        d.update(
            id=self.id,
            name=self.name,
            flds=self.fields,
            tmpls=self.templates,
            mod=int(time()),
            type=type_,
            req=req
        )
        d.update(kwargs)

        super(ModelBuilder, self).__init__(d)

    @property
    def field_names(self):
        return [f.name for f in self.fields]

    @property
    def template_names(self):
        return [t.name for t in self.templates]


class FieldBuilder(dict):
    """
    "JSONArray containing object for each field in the model as follows:",
     {
       font : "display font",
       media : "array of media. appears to be unused",
       name : "field name",
       ord : "ordinal of the field - goes from 0 to num fields -1",
       rtl : "boolean, right-to-left script",
       size : "font size",
       sticky : "sticky fields retain the value that was last added
                   when adding new notes"
     }
    """
    def __init__(self, name, order, **kwargs):
        self.name = name
        self.order = order
        d = next(iter(default['col']['models'].values()))['flds'][0].copy()
        d.update(
            name=self.name,
            ord=self.order,
            **kwargs
        )

        super(FieldBuilder, self).__init__(d)


class TemplateBuilder(dict):
    """
    "JSONArray containing object of CardTemplate for each card in model",
      {
        afmt : "answer template string",
        bafmt : "browser answer format:
                  used for displaying answer in browser",
        bqfmt : "browser question format:
                  used for displaying question in browser",
        did : "deck override (null by default)",
        name : "template name",
        ord : "template number, see flds",
        qfmt : "question format string"
      }
    """
    def __init__(self, name, question, answer, order, **kwargs):
        self.name = name
        self.question = question
        self.answer = answer
        self.order = order
        d = next(iter(default['col']['models'].values()))['tmpls'][0].copy()
        d.update(
            name=self.name,
            qfmt=self.question,
            afmt=self.answer,
            ord=self.order,
            **kwargs
        )

        super(TemplateBuilder, self).__init__(d)
