from datetime import date

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from listsapp.models import Degree, Rule, Faculty, Specialty, AcademicPlan, Subject

User = get_user_model()

SELECT_CLASS = """disabled:opacity-50 mt-1 mr-3 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md 
                shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm """
INPUT_CLASS = """disabled:opacity-50 mt-1 mr-3 py-2 px-3 focus:ring-indigo-500 focus:border-indigo-500 block w-full 
                shadow-sm sm:text-sm border border-gray-300 rounded-md """
CHECK_CLASS = """disabled:opacity-50 mt-1 mr-3 py-2 px-3 focus:ring-indigo-500 focus:border-indigo-500 block w-1/6 
                shadow-sm sm:text-sm border border-gray-300 rounded-md """
HOURS_CLASS = """disabled:opacity-50 mt-0.5 mx-1.5 py-1.5 px-2 focus:ring-indigo-500 focus:border-indigo-500 block 
                w-3/12 shadow-sm sm:text-sm border border-gray-300 rounded-md """
SUBJECT_CLASS = """disabled:opacity-50 mt-0.5 mx-1.5 py-1.5 px-2 focus:ring-indigo-500 focus:border-indigo-500 block 
                w-full shadow-sm sm:text-sm border border-gray-300 rounded-md """


class SubjectConflictSolve(forms.Form):
    subject = forms.CharField(label='', max_length=240,
                              widget=forms.TextInput(attrs={'class': INPUT_CLASS}))
    is_create = forms.BooleanField(label='', required=False,
                                   widget=forms.CheckboxInput(attrs={'class': CHECK_CLASS}))
    sub_likes = forms.ChoiceField(label="", required=False, widget=forms.Select(attrs={'class': SELECT_CLASS}))

    def __init__(self, *args, **kwargs):
        if kwargs.get('initial'):
            sim = kwargs.get('initial').get('likes_choices')
            self.base_fields['sub_likes'].choices = [(_[1].id, _[1]) for _ in sim]
        super(SubjectConflictSolve, self).__init__(*args, **kwargs)

    def set_similar(self, sim: list):
        self.fields['sub_likes'].choices = [(_[1].id, _[1]) for _ in sim]
        # self.errors = None

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['is_create']:
            if not cleaned_data.get('subject'):
                raise ValidationError({'subject': _('Нельзя создать дисциплину без названия')})

            if Subject.objects.filter(subject=self.cleaned_data.get("subject")):
                raise ValidationError({'subject': _('Такая дисциплина уже существует. Измените название дисциплины '
                                                    'или свяжите с существующей')})

        else:
            if not cleaned_data.get("sub_likes"):
                raise ValidationError({'sub_likes': _('Нельзя связать ни с какой дисциплиной. Пожалуйста, добавьте '
                                                      'новую')})


class PlanItemUpload(forms.ModelForm):
    class Meta:
        model = AcademicPlan
        # fields = '__all__'
        fields = ['semester', 'id_subject', 'h_lecture', 'h_laboratory', 'h_practice', 'control', 'id_specialty']

        labels = {
            'semester': _(''),
            'id_subject': _(''),
            'h_laboratory': _(''),
            'h_lecture': _(''),
            'h_practice': _(''),
            'control': _(''),
        }

        widgets = {
            'semester': forms.NumberInput(
                attrs={
                    'class': HOURS_CLASS,
                    'type': "number",
                    'value': '1',
                    'min': '1',
                    'max': AcademicPlan.MAX_SEMESTER
                }),
            'h_laboratory': forms.NumberInput(
                attrs={
                    'class': HOURS_CLASS,
                    'type': "number",
                    'value': '0',
                    'min': '0',
                    'max': '9',
                }),
            'h_lecture': forms.NumberInput(
                attrs={
                    'class': HOURS_CLASS,
                    'type': "number",
                    'value': '0',
                    'min': '0',
                    'max': '9',
                }),
            'h_practice': forms.NumberInput(
                attrs={
                    'class': HOURS_CLASS,
                    'type': "number",
                    'value': '0',
                    'min': '0',
                    'max': '9',
                }),
            'control': forms.Select(attrs={'class': HOURS_CLASS}),
            'id_specialty': forms.TextInput(
                attrs={
                    'class': INPUT_CLASS,
                    'type': "hidden",
                    'value': '1',
                }),
            'id_subject': forms.Select(
                attrs={
                    'class': SUBJECT_CLASS,
                    # 'disabled': True,
                }),
        }


class SubjectFilterForm(forms.Form):
    specialty = forms.ModelChoiceField(label="Специальность",
                                       queryset=Specialty.objects.all(),
                                       widget=forms.Select(attrs={'class': SELECT_CLASS}))
    semester = forms.ChoiceField(label="Семестр", widget=forms.Select(attrs={'class': SELECT_CLASS}))

    def __init__(self, years, *args, **kwargs):
        super().__init__()
        self.fields['semester'].choices = [(i, i + 1) for i in range(years * 2)]

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
    page = forms.ChoiceField(label="Страница из файла", required=True,
                             widget=forms.Select(attrs={'class': SELECT_CLASS}))

    def clear(self):
        super(UploadFileForm, self).clear()
        if Specialty.objects.filter(specialty=self.cleaned_data.get("specialty")):
            raise ValidationError({'subject': _('Такая дисциплина уже существует. Измените название дисциплины '
                                                'или свяжите с существующей')})

    def set_page(self, page):
        self.fields['page'].choices = [(page, page), ]
