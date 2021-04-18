from datetime import date

from django import forms
from django.contrib.auth import get_user_model

from listsapp.models import Degree, Rule, Faculty, Specialty, AcademicPlan

User = get_user_model()

SELECT_CLASS = """disabled:opacity-50 mt-1 mr-3 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm 
                                    focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"""
INPUT_CLASS = """disabled:opacity-50 mt-1 mr-3 py-2 px-3 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm 
                                    sm:text-sm border border-gray-300 rounded-md"""
CHECK_CLASS = """disabled:opacity-50 mt-1 mr-3 py-2 px-3 focus:ring-indigo-500 focus:border-indigo-500 block w-1/6 shadow-sm 
                                    sm:text-sm border border-gray-300 rounded-md"""


class SubjectConflictSolve(forms.Form):
    CHOICE = [(True, 'Да'), (False, 'Нет')]

    subject = forms.CharField(label='', max_length=240,
                              widget=forms.TextInput(attrs={'class': INPUT_CLASS}))
    is_create = forms.ChoiceField(label='', label_suffix='', choices=CHOICE,
                                  widget=forms.Select(attrs={'class': CHECK_CLASS}))
    sub_likes = forms.ChoiceField(label="", widget=forms.Select(attrs={'class': SELECT_CLASS}))

    def set_similar(self, sim: list):
        self.fields['sub_likes'].choices = [(_[1].id, _[1]) if sim[0] else ('0', 'Нет') for _ in sim ]


class PlanItemUpload(forms.Form):
    semester = forms.IntegerField(label='',
                                  widget=forms.NumberInput(
                                      attrs={
                                          'class': INPUT_CLASS,
                                          'type': "number",
                                          'value': '1',
                                          'min': '1',
                                          'max': AcademicPlan.MAX_SEMESTER
                                      }))
    subject = forms.CharField(label='', max_length=240,
                              widget=forms.TextInput(attrs={'class': INPUT_CLASS}))
    is_create = forms.BooleanField(label='', required=False,
                                   widget=forms.CheckboxInput(attrs={'class': CHECK_CLASS}))
    sub_likes = forms.ChoiceField(label="", widget=forms.Select(attrs={'class': SELECT_CLASS, 'required': False}))
    h_lec = forms.IntegerField(label='',
                               widget=forms.NumberInput(
                                   attrs={
                                          'class': INPUT_CLASS,
                                          'type': "number",
                                          'value': '0',
                                          'min': '0',
                                      }))
    h_lab = forms.IntegerField(label='',
                               widget=forms.NumberInput(
                                   attrs={
                                       'class': INPUT_CLASS,
                                       'type': "number",
                                       'value': '0',
                                       'min': '0',
                                   }))
    h_prac = forms.IntegerField(label='',
                                widget=forms.NumberInput(
                                   attrs={
                                       'class': INPUT_CLASS,
                                       'type': "number",
                                       'value': '0',
                                       'min': '0',
                                   }))
    control = forms.ChoiceField(label="",
                                choices=AcademicPlan.CONTROLS,
                                widget=forms.Select(attrs={'class': SELECT_CLASS}))

    def set_similar(self, sim: list):
        self.fields['sub_likes'].choices = [(_[1].id, _[1]) for _ in sim]
        pass


class SubjectFilterForm(forms.Form):
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
    page = forms.ChoiceField(label="Страница из файла", required=True, widget=forms.Select(attrs={'class': SELECT_CLASS}))

    def set_page(self, page):
        self.fields['page'].choices = [(page, page), ]
