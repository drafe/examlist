from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField

from datetime import date
from pathlib import Path

from listsapp.models import Degree, Rule, Faculty, Specialty

User = get_user_model()

SELECT_CLASS = """disabled:opacity-50 mt-1 mr-3 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm 
                                    focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"""
INPUT_CLASS = """disabled:opacity-50 mt-1 mr-3 py-2 px-3 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm 
                                    sm:text-sm border border-gray-300 rounded-md"""


class SubjectFilterForm(forms.Form):
    # faculty = forms.ModelChoiceField(label="Факультет", queryset=Faculty.objects.all(),
    #                                  widget=forms.Select(attrs={'class': SELECT_CLASS}))
    specialty = forms.ModelChoiceField(label="Специальность",
                                       queryset=Specialty.objects.all(),
                                       widget=forms.Select(attrs={'class': SELECT_CLASS}))
    semester = forms.ChoiceField(label="Семестр", widget=forms.Select(attrs={'class': SELECT_CLASS}))

    def __init__(self, years, *args, **kwargs):
        super().__init__()
        self.fields['semester'].choices = [(i, i+1) for i in range(years*2)]
    pass


class SubjectFilterUserForm(SubjectFilterForm):
    year = forms.IntegerField(label='Начало учебного года', widget=forms.NumberInput(
        attrs={'class': INPUT_CLASS, 'type': "number", 'value': date.today().year}))
    # year_end = forms.IntegerField(label='', widget=forms.NumberInput(
    #     attrs={'class': INPUT_CLASS, 'type': "number", 'readonly': True}))

    def __init__(self, *args, **kwargs):
        super().__init__(years=0)
        self.fields['semester'].choices = [(0, 'Осень'), (1, 'Весна')]


class UploadFileForm(forms.Form):
    prefix = 'upload'

    file = forms.FileField(label='', )
    specialty = forms.CharField(label="Новая специальность", max_length=240,
                                widget=forms.TextInput(attrs={'class': INPUT_CLASS}))
    faculty = forms.ModelChoiceField(label="Факультет", queryset=Faculty.objects.all(),
                                     widget=forms.Select(attrs={'class': SELECT_CLASS}))
    degree = forms.ModelChoiceField(label="Образовательный уровень", queryset=Degree.objects.all(),
                                    widget=forms.Select(attrs={'class': SELECT_CLASS}))
    rule = forms.ModelChoiceField(label="Правило для файла", queryset=Rule.objects.all(),
                                  widget=forms.Select(attrs={'class': SELECT_CLASS}))
    page = forms.ChoiceField(label="Страница из файла", widget=forms.Select(attrs={'class': SELECT_CLASS}))

    def set_page(self, page):
        self.fields['page'].choices = [(page, page), ]
