from django import forms
from .models import Settings
from django.core.exceptions import ValidationError
import re

from .TrelloToMongoAdapter import getDB
from .TrelloUtility import TrelloUtility
from .MongoDBUtility import getLists, getLabels, getMembers

from .APIKey import apiKey


class BoardForm(forms.Form):
    link = forms.URLField()
    link.widget.attrs.update({'class': 'form-control'})
    boardID = ""
    boardName = ""
    tokenKey = ""

    def clean_link(self):
        try:
            match = re.search(r'https://trello.com/b/(?P<boardID>\w+)/(?P<boardName>\w+)', self.cleaned_data['link'])
            self.boardID = match.group('boardID')
            self.boardName = match.group('boardName')
            #data = TrelloUtility(api=apiKey, token=self.tokenKey).sendRequest("boards/{}".format(self.boardID), "id")
        except Exception as err:
            print(err)
            raise ValidationError('Incorrect link!')
        return self.cleaned_data['link']

    def save(self):
        return {'boardID': self.boardID, 'boardName': self.boardName}


class ToLists:
    def __init__(self):
        db = getDB()
        self.Lists = []
        self.Labels = []
        self.Members = []
        tmp = getLists(db)
        for d in tmp:
            self.Lists.append((d['name'], d['name']))
        tmp = getLabels(db)
        for d in tmp:
            self.Labels.append(("{color},{name}".format(color=d['color'], name=d['name']),
                               "{color} ({name})".format(color=d['color'], name=d['name'])))
        tmp = getMembers(db)
        for d in tmp:
            self.Members.append(("{fullName},{username}".format(fullName=d['fullName'], username=d['username']),
                                "{fullName} ({username})".format(fullName=d['fullName'], username=d['username'])))

class SettingsForm(forms.Form):
    lists = ToLists()
    start_list = forms.TypedMultipleChoiceField(choices=lists.Lists)
    start_list.widget.attrs.update({'class': 'custom-select my-1 mr-2'})
    final_list = forms.TypedMultipleChoiceField(choices=lists.Lists)
    final_list.widget.attrs.update({'class': 'custom-select my-1 mr-2'})
    key_words = forms.CharField(required=False)
    key_words.widget.attrs.update({'class': 'form-control'})
    labels = forms.TypedMultipleChoiceField(choices=lists.Labels)
    labels.widget.attrs.update({'class': 'custom-select my-1 mr-2'})
    executors = forms.TypedMultipleChoiceField(choices=lists.Members)
    executors.widget.attrs.update({'class': 'custom-select my-1 mr-2'})
    attachment = forms.BooleanField(required=False)
    attachment.widget.attrs.update({'class': 'form-check-input'})
    comments = forms.BooleanField(required=False)
    comments.widget.attrs.update({'class': 'form-check-input'})
    from_date = None
    to_date = None
    due_date = None


    def save(self, due_date, from_date, to_date):
        self.from_date = from_date
        self.to_date = to_date
        self.due_date = due_date
        new_settings = Settings(start_list=self.cleaned_data['start_list'],
                                final_list=self.cleaned_data['final_list'],
                                key_words=self.cleaned_data['key_words'].split(' '),
                                labels=self.cleaned_data['labels'],
                                executors=self.cleaned_data['executors'],
                                due_date=due_date,
                                from_date=from_date,
                                to_date=to_date,
                                attachment=self.cleaned_data['attachment'],
                                comments=self.cleaned_data['comments'])
        return new_settings