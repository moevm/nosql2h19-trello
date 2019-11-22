from django import forms
from .models import Link, Settings

class LinkForm(forms.Form):
    link = forms.URLField()

    link.widget.attrs.update({'class': 'form-control'})

    def save(self):
        # Тут наверное неплохо было бы проверить ссылочку
        new_link = Link(link=self.cleaned_data['link'])
        return new_link


class SettingsForm(forms.Form):
    lists = ((0, 'Список 0'), (1, 'Список 1'), (2, 'Список 2')) # Денис: cюда необходимо поместить названия списков из бд и индивидуальный номер для них, чтобы можно было идентифицировать что выбрал пользователь в форме
    start_list = forms.TypedMultipleChoiceField(choices=lists)
    start_list.widget.attrs.update({'class': 'custom-select my-1 mr-2'})
    final_list = forms.TypedMultipleChoiceField(choices=lists)
    final_list.widget.attrs.update({'class': 'custom-select my-1 mr-2'})
    key_words = forms.CharField(required=False)
    key_words.widget.attrs.update({'class': 'form-control'})
    labels_list = ((0, 'Метка 0'), (1, 'Метка 1'), (2, 'Метка 2')) # Денис: cюда необходимо поместить названия меток (с названием цветов?) из бд и индивидуальный номер для них, чтобы можно было идентифицировать что выбрал пользователь в форме
    labels = forms.TypedMultipleChoiceField(choices=labels_list)
    labels.widget.attrs.update({'class': 'custom-select my-1 mr-2'})
    executors_list = ((0, 'Пользователь 0'), (1, 'Пользователь 1'), (2, 'Пользователь 2')) # Денис: cюда необходимо поместить список пользователей из бд и индивидуальный номер для них, чтобы можно было идентифицировать что выбрал пользователь в форме
    executors = forms.TypedMultipleChoiceField(choices=executors_list)
    executors.widget.attrs.update({'class': 'custom-select my-1 mr-2'})
    due_date = forms.DateField()
    due_date.widget.attrs.update({'class': 'form-control'})
    from_date = forms.DateField()
    from_date.widget.attrs.update({'class': 'form-control'})
    to_date = forms.DateField()
    to_date.widget.attrs.update({'class': 'form-control'})
    attachment = forms.BooleanField(required=False)
    attachment.widget.attrs.update({'class': 'form-check-input'})
    comments = forms.BooleanField(required=False)
    comments.widget.attrs.update({'class': 'form-check-input'})

    def save(self):
        # тут нужно проверить что даты до и после нормальные

        new_settings = Settings(start_list=self.cleaned_data['start_list'],
                                final_list=self.cleaned_data['final_list'],
                                key_words=self.cleaned_data['key_words'],
                                labels=self.cleaned_data['labels'],
                                executors=self.cleaned_data['executors'],
                                due_date=self.cleaned_data['due_date'],
                                from_date=self.cleaned_data['from_date'],
                                to_date=self.cleaned_data['to_date'],
                                attachment=self.cleaned_data['attachment'],
                                comments=self.cleaned_data['comments'])
        return new_settings