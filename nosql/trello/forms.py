from django import forms
from .models import Settings
from django.core.exceptions import ValidationError
import re

from .TrelloToMongoAdapter import getDB
from .TrelloUtility import TrelloUtility
from .MongoDBUtility import getLists, getLabels, getMembers

from .APIKey import apiKey


class FileForm(forms.Form):
    file = forms.FileField()


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


class SettingsForm(forms.Form):
    # start_list = forms.TypedMultipleChoiceField(choices=lists.Lists)
    start_list = forms.TypedMultipleChoiceField()
    start_list.widget.attrs.update({'class': 'custom-select my-1 mr-2'})
    key_words = forms.CharField(required=False)
    key_words.widget.attrs.update({'class': 'form-control'})
    # labels = forms.TypedMultipleChoiceField(choices=lists.Labels)
    labels = forms.TypedMultipleChoiceField()
    labels.widget.attrs.update({'class': 'custom-select my-1 mr-2'})
    # executors = forms.TypedMultipleChoiceField(choices=lists.Members)
    executors = forms.TypedMultipleChoiceField()
    executors.widget.attrs.update({'class': 'custom-select my-1 mr-2'})
    attachment = forms.BooleanField(required=False)
    attachment.widget.attrs.update({'class': 'form-check-input'})
    comments = forms.BooleanField(required=False)
    comments.widget.attrs.update({'class': 'form-check-input'})
    from_date = None
    to_date = None
    due_date = None

    def __init__(self, lists=[], labels=[], members=[], *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self.fields['start_list'].choices = lists
        self.fields['labels'].choices = labels
        self.fields['executors'].choices = members
