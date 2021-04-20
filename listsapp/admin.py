from django.contrib import admin
from .models import Degree, Specialty, Subject, AcademicPlan, Group, Rule, Faculty


# Register your models here.
class DegreeAdmin(admin.ModelAdmin):
    list_display = ['degree', ]


class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['specialty', 'id_faculty', 'id_degree']
    list_filter = ['id_faculty', ]


class SubjectAdmin(admin.ModelAdmin):
    list_display = ['subject', ]


class AcademicAdmin(admin.ModelAdmin):
    list_display = ['semester', 'control', 'id_specialty', 'id_subject',
                    'h_laboratory', 'h_lecture', 'h_practice']
    list_filter = ['id_specialty', 'semester', 'control', ]


class GroupAdmin(admin.ModelAdmin):
    list_display = ['enter_year', 'id_specialty', 'name']
    list_filter = ['id_specialty', ]


class RuleAdmin(admin.ModelAdmin):
    list_display = ['rule_name', 'rule']


class FacultyAdmin(admin.ModelAdmin):
    list_display = ['faculty']


admin.site.register(Degree, DegreeAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Specialty, SpecialtyAdmin)
admin.site.register(AcademicPlan, AcademicAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(Faculty, FacultyAdmin)
