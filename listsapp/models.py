from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

from schema import Schema, And, Use


class Degree(models.Model):
    degree = models.CharField(max_length=50)

    def __str__(self):
        return self.degree


class Faculty(models.Model):
    faculty = models.CharField(max_length=240, unique=True)

    def __str__(self):
        return self.faculty


class Specialty(models.Model):
    id_degree = models.ForeignKey('Degree', on_delete=models.PROTECT)
    id_faculty = models.ForeignKey('Faculty', on_delete=models.PROTECT, default=1)
    specialty = models.CharField(max_length=240, unique=True)

    def __str__(self):
        return self.specialty


class Subject(models.Model):
    subject = models.CharField(max_length=240, unique=True)

    def __str__(self):
        return self.subject


class AcademicPlan(models.Model):
    EXAM = 'exam'
    QUIZ = 'quiz'
    M_QU = 'm_qu'
    CONTROLS = [
        (EXAM, 'Экзамен'),
        (QUIZ, 'Зачёт'),
        (M_QU, 'Диф. зачёт')
    ]
    MAX_SEMESTER = 8

    semester = models.PositiveIntegerField()
    control = models.CharField(max_length=4, choices=CONTROLS)
    id_specialty = models.ForeignKey('Specialty', on_delete=models.PROTECT)
    id_subject = models.ForeignKey('Subject', on_delete=models.PROTECT)
    h_laboratory = models.PositiveIntegerField()
    h_lecture = models.PositiveIntegerField()
    h_practice = models.PositiveIntegerField()

    def clean(self):
        # Don't allow draft entries to have a pub_date.
        if self.semester == 0:
            raise ValidationError({'semester': _('Отсчет семестров начинается с 1')})
        elif self.semester > self.MAX_SEMESTER:
            raise ValidationError({'semester': _(f'Максимальное значение для семестра равно {self.MAX_SEMESTER}')})


class Group(models.Model):
    enter_year = models.PositiveIntegerField(default=2020)
    id_specialty = models.ForeignKey('Specialty', on_delete=models.PROTECT)
    name = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.name}-{self.enter_year} -- {self.id_specialty}"


class Rule(models.Model):
    rule_name = models.CharField(max_length=120)
    rule = models.JSONField()

    RULE_SCHEMA = Schema({'columns': {
        'cipher': And(str, Use(str.upper), lambda s: s.isalpha()),
        'subjects': And(str, Use(str.upper), lambda s: s.isalpha()),
        'departments': And(str, Use(str.upper), lambda s: s.isalpha()),
        'controls': {
            'exam': And(str, Use(str.upper), lambda s: s.isalpha()),
            'quiz': And(str, Use(str.upper), lambda s: s.isalpha()),
            'course': And(str, Use(str.upper), lambda s: s.isalpha())
        },
        '1_sem': And(str, Use(str.upper), lambda s: s.isalpha()),
        'lectures': And(int),
        'practice': And(int),
        'labs': And(int)},
        'ciphers': And(list, lambda x: map(str, x))})
    JSON_FORMAT_ERROR = '''Формат JSON должен быть следующим: 
    "Физтех Очная": {
      "columns": {
         "cipher": "A",
         "subjects": "B",
         "departments": "BG",
         "controls": {
            "exam": "C",
            "quiz": "D",
            "course": "E"
         },
         "1_sem": "R",
         "lectures": 1,
         "practice": 2,
         "labs": 3
      },
      "ciphers": [
         "ОНБ",
         "ПБ"
      ]
   },'''

    def __str__(self):
        return f"{self.rule_name}"

    def clean(self):
        if self.RULE_SCHEMA.validate(self.rule):
            raise ValidationError({'rule': _(self.JSON_FORMAT_ERROR)})


class AdminMessage(models.Model):
    topic = models.CharField(max_length=120)
    mail = models.EmailField()
    text = models.TextField()
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    is_solve = models.BooleanField(default=False)

