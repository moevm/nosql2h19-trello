from django.db import models

class Link():
    def __init__(self, link):
        self.link = link


class Settings():
    def __init__(self, start_list, final_list, key_words, labels, executors, due_date, from_date, to_date, attachment, comments):
        self.start_list = start_list
        self.final_list = final_list
        self.key_words = key_words
        self.labels = labels
        self.executors = executors
        self.due_date = due_date
        self.from_date = from_date
        self.to_date = to_date
        self.attachment = attachment
        self.comments = forms.comments
