from django.db import models
from django.contrib.auth.models import AbstractUser


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
    specialty = models.CharField(max_length=240)

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
    semester = models.PositiveIntegerField()
    control = models.CharField(max_length=4, choices=CONTROLS)
    id_specialty = models.ForeignKey('Specialty', on_delete=models.PROTECT)
    id_subject = models.ForeignKey('Subject', on_delete=models.PROTECT)
    h_laboratory = models.PositiveIntegerField()
    h_lecture = models.PositiveIntegerField()
    h_practice = models.PositiveIntegerField()


class Group(models.Model):
    enter_year = models.PositiveIntegerField(default=2020)
    id_specialty = models.ForeignKey('Specialty', on_delete=models.PROTECT)
    name = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.name}-{self.enter_year} -- {self.id_specialty}"


class Rule(models.Model):
    rule_name = models.CharField(max_length=120)
    rule = models.JSONField()

    def __str__(self):
        return f"{self.rule_name}"
