from functools import reduce

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.forms import formset_factory, BaseFormSet, modelformset_factory
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView

from .forms import UploadFileForm, SubjectFilterForm, SubjectFilterUserForm, PlanItemUpload, SubjectConflictSolve
from .models import AcademicPlan, Specialty, Group, Rule, Subject

from .functionality.upload import Parser, FuzzySubjectsComparison


# Create your views here.


def home(request):
    return render(request, 'home.html')


def logout_request(request):
    logout(request)
    return redirect('home')


@method_decorator(login_required, name='dispatch')
class PlanItemsCreateView(View):
    row_data = dict()
    template_name = 'upload_items.html'
    PlanItemsFormSet = modelformset_factory(AcademicPlan, form=PlanItemUpload)

    def init_item(self, init, item, control, spec_name):
        init[item[0]]['semester'] = item[1]
        init[item[0]]['h_lecture'] = item[2]
        init[item[0]]['h_laboratory'] = item[3]
        init[item[0]]['h_practice'] = item[4]
        init[item[0]]['control'] = control
        init[item[0]]['id_specialty'] = Specialty(specialty=spec_name)

    def init_forms(self, request):
        request.session['row_data'] = self.row_data
        subj = self.row_data.get('subjects')
        spec = self.row_data.get('specialty')
        init = [{'id_subject': Subject.objects.get(id=_)} for _ in subj]
        for e in self.row_data.get('exam'):
            self.init_item(init, e, AcademicPlan.EXAM, spec)

        for q in self.row_data.get('quiz'):
            self.init_item(init, e, AcademicPlan.QUIZ, spec)

        for mq in self.row_data.get('m_qu'):
            self.init_item(init, e, AcademicPlan.M_QU, spec)

        formset = PlanItemUpload(initial=init)
        formset.forms = formset.initial_forms
        return formset

    def get(self, request):

        self.row_data = request.session.pop("row_data", None)
        if self.row_data is None:
            raise Http404('')

        formset = self.init_forms(request)
        return render(request, self.template_name, {'plan_formset': formset})

    def post(self, request):
        self.row_data = request.session.pop("row_data", None)
        if self.row_data is None:
            raise Http404('')

        formset = self.PlanItemsFormSet(request.POST)
        formset.forms = formset.initial_forms
        request.session['row_data'] = self.row_data

        if formset.is_valid():
            # todo создать и перенаправить
            spec = Specialty(id_faculty=self.row_data.get('faculty'), specialty=self.row_data.get('specialty'))
            spec.save()
            for form in formset:
                form.fields['id_specialty'] = spec.id
                form.save()

            return redirect('home')

        context = dict(subject_formset=formset)
        return render(request, self.template, context)


class BaseSubjectFormSet(BaseFormSet):

    def set_total_via_init(self):
        self.forms = self.initial_forms

    def clean(self):
        super().clean()
        if any(self.errors):
            return

        new_subjects = []
        for form in self.forms:
            subj = form.cleaned_data.get('subject')
            flag = form.cleaned_data.get('is_create')
            if flag and subj in new_subjects:
                raise ValidationError("Нельзя создать две дисциплины с одним названием!")
            new_subjects.append(subj)


@method_decorator(login_required, name='dispatch')
class SubjectConflictView(View):
    row_data = dict()
    forms = list()
    SubjectFormSet = formset_factory(SubjectConflictSolve, formset=BaseSubjectFormSet)
    template = 'upload_conflicts.html'

    def init_forms(self):
        similars = FuzzySubjectsComparison(self.row_data.get('subjects')).compareAll()
        init = [dict(likes_choices=lc, subject=_) for _, lc in zip(self.row_data.get('subjects'), similars)]
        return init

    def get(self, request):
        self.row_data = request.session.pop("row_data", None)
        if self.row_data is None:
            # row_data = {
            #     'subjects': ['Иностранный язык', 'История', 'Философия', 'Иностранный язык в профессиональной сфере',
            #                  'Математика', 'Физика', 'Информатика и информационно-коммуникационные технологии',
            #                  'Правоведение', 'Экономика', 'Дискретная математика',
            #                  'Теория  вероятности, математическая статистика', 'Физическая  культура',
            #                  'Русский язык и культура речи', 'Естественнонаучная картина мира', 'Психология',
            #                  'Экология', 'Метрология, стандартизация и сертификация', 'Математическая логика',
            #                  'История науки и техники / Культурология', 'Методика преподавания / Педагогика',
            #                  'Социология и политология / Религиоведение', 'Операционные системы',
            #                  'Электротехника, электроника и схемотехника', 'Базы данных', 'Сети и телекоммуникации',
            #                  'Основы программирования', 'Безопасность жизнедеятельности', 'Основы охраны труда',
            #                  'Курсовая работа по дисциплине "Базы данных"', 'Программирование', 'Web-программирование',
            #                  'СУБД Oracle', 'Объектно-ориентированное программирование',
            #                  'Современные информационные системы и технологии', 'Инженерная и компьютерная графика',
            #                  'Архитектура ЭВМ и микроконтроллеров', 'ЭВМ и периферийные устройства',
            #                  'Программирование на языках низкого уровня', 'Защита информации',
            #                  'Методы и средства проектирования информационных систем и технологий',
            #                  'Технологии разработки программного обеспечения',
            #                  'Тестирование и внедрение программного обеспечения',
            #                  'Курсовая работа по дисциплине "Программирование"',
            #                  'Курсовая работа по дисциплине "Web-программирование"',
            #                  'Программирование в системе "1С: Предприятие" / Администрирование системы "1С: Предприятие" / Компьютерный дизайн',
            #                  'Вычислительная математика  / Численные методы /Вычислительные методы',
            #                  'Программирование робототехнических систем / Администрирование операционных систем /  Программные средства обработки графической информации',
            #                  'Интернет-технологии /  Аппаратные средства локальных сетей / Web-дизайн',
            #                  'Программирование в Unix / Администрирование распределённых систем / Компьютерная анимация и видео'],
            #     'exam': [[0, 2, 0, 3, 0], [1, 1, 2, 0, 1], [2, 4, 1, 0, 1], [3, 4, 0, 0, 2], [4, 1, 3, 0, 3],
            #              [4, 2, 3, 0, 3], [5, 1, 2, 2, 0], [5, 2, 2, 2, 0], [6, 1, 1, 2, 0], [9, 2, 1, 0, 2],
            #              [10, 3, 1, 0, 2], [12, 2, 1, 0, 2], [12, 3, 1, 0, 2], [21, 5, 2, 2, 0], [21, 6, 1, 3, 0],
            #              [22, 3, 1, 2, 0], [22, 4, 1, 2, 0], [23, 5, 2, 2, 0], [24, 5, 2, 2, 0], [24, 6, 2, 2, 0],
            #              [25, 1, 2, 2, 0], [26, 3, 2, 0, 0], [27, 4, 1, 0, 1], [29, 3, 2, 2, 0], [29, 4, 2, 2, 0],
            #              [30, 6, 2, 2, 0], [32, 8, 1, 2, 0], [33, 7, 2, 2, 0], [33, 8, 2, 2, 0], [36, 4, 2, 2, 0],
            #              [39, 7, 2, 2, 0], [44, 8, 2, 4, 0], [45, 5, 2, 2, 0], [46, 6, 2, 2, 0], [47, 7, 2, 4, 0],
            #              [48, 8, 2, 2, 0]],
            #     'quiz': [[0, 1, 0, 2, 0], [3, 3, 0, 0, 1], [6, 2, 2, 2, 0], [7, 6, 1, 0, 2], [8, 7, 1, 0, 2],
            #              [11, 1, 2, 0, 0], [12, 1, 1, 0, 2], [13, 1, 2, 0, 0], [14, 2, 1, 0, 2], [15, 5, 1, 0, 2],
            #              [16, 7, 1, 0, 1], [17, 4, 1, 0, 2], [18, 3, 1, 0, 2], [19, 6, 1, 0, 2], [20, 5, 1, 0, 1],
            #              [23, 4, 2, 2, 0], [25, 2, 2, 2, 0], [30, 5, 1, 2, 0], [31, 8, 2, 2, 0], [32, 7, 2, 2, 0],
            #              [35, 3, 2, 2, 0], [37, 5, 1, 2, 0], [38, 7, 1, 0, 2], [40, 3, 1, 2, 0], [41, 6, 1, 2, 0],
            #              [46, 5, 1, 1, 0], [48, 7, 1, 2, 0]],
            #     'm_qu': [[34, 3, 2, 2, 0], [34, 4, 1, 2, 0]]}
            raise Http404('')
        request.session['row_data'] = self.row_data

        init = self.init_forms()
        formset = self.SubjectFormSet(initial=init)
        formset.set_total_via_init()

        context = dict(subject_formset=formset)
        return render(request, self.template, context)

    def post(self, request):
        self.row_data = request.session.pop("row_data", None)
        if self.row_data is None:
            raise Http404('')
        request.session['row_data'] = self.row_data

        init = self.init_forms()
        formset = self.SubjectFormSet(request.POST, initial=init)
        formset.set_total_via_init()

        if formset.is_valid():
            subj = list()
            for _ in formset.cleaned_data:
                if _['is_create']:
                    s = Subject(subject=_['subject'])
                    s.save()
                    subj.append(s.id)
                else:
                    subj.append(int(_['sub_likes']))

            self.row_data['subjects'] = subj
            request.session['row_data'] = self.row_data
            return redirect('upload_items')

        context = dict(subject_formset=formset)
        return render(request, self.template, context)


@login_required
def upload_file(request):
    context = {'upload': UploadFileForm()}
    if request.method == 'POST':
        upload_form = UploadFileForm(request.POST, request.FILES)
        upload_form.set_page(request.POST.get('upload-page'))
        if upload_form.is_valid():
            file = upload_form.cleaned_data['file']
            rule = upload_form.cleaned_data['rule'].rule
            page = upload_form.cleaned_data['page']
            row_data = Parser(file, page, rule).parse()
            row_data['specialty'] = upload_form.cleaned_data['specialty']
            row_data['faculty'] = upload_form.cleaned_data['faculty'].id

            # context = {'upload_items': [PlanItemUpload() for i in range(3)]}
            request.session['row_data'] = row_data
            request.session['key'] = True
            return redirect('upload_conflicts')
        else:
            context['upload'] = upload_form

    return render(request, 'upload_file.html', context)


def subjects_filter(request):
    try:
        sp = request.GET.get('specialty')
        sem = request.GET.get('semester') + 1
    except:
        qs = None
    else:
        qs = AcademicPlan.objects.select_related('id_specialty', 'id_subject').all()
        qs = qs.filter(id_specialty=sp).filter(semester=sem).order_by('control')
        spec = Specialty.objects.select_related('id_faculty').get(id=sp)
        context = {'subjects': qs,
                   'title': f"{spec.id_faculty} {spec} {sem} семестр",
                   }
        return context


def subjects_user_filter(request):
    try:
        spec = int(request.GET.get('specialty'))
        sem = int(request.GET.get('semester'))
        year = int(request.GET.get('year'))
    except:
        qs = None
    else:
        semesters = [i for i in range(1, AcademicPlan.MAX_SEMESTER + 1) if i % 2 != sem]
        gr = Group.objects.select_related('id_specialty') \
            .filter(id_specialty=spec) \
            .filter(enter_year__range=(year - 3, year)) \
            .values('enter_year').annotate(count=Count('id'))

        qs = AcademicPlan.objects.select_related('id_specialty', 'id_subject') \
            .filter(id_specialty=spec) \
            .filter(semester__in=semesters) \
            .order_by('semester')

        s = {}
        for q in qs:
            if q.semester in s:
                s[q.semester].append(q)
            else:
                s[q.semester] = [q, ]

        subjects = [{'course': (i + 1 // 2), 'subjects': s[i]} for i in s]
        if len(gr) < len(s):
            for i, g in enumerate(gr):
                subjects[i]['groups'] = g['count']
        else:
            for i, g in enumerate(gr[:len(s)]):
                subjects[i]['groups'] = g['count']

        sp = Specialty.objects.select_related('id_faculty').get(id=spec)
        sem = 'осенний' if int(request.GET['semester']) == 0 else 'весенний'
        context = {'subjects': subjects,
                   'title': f"{sp.id_faculty} {sp} : {year}-{year + 1} уч.год {sem} семестр"
                   }
        return context


def SubjectsFilterView(request):
    context = {}
    if request.GET:
        if request.user.is_authenticated:
            context = subjects_user_filter(request)
        else:
            context = subjects_filter(request)

    if request.user.is_authenticated:
        context['filter_form'] = SubjectFilterUserForm()
        return render(request, "subjects_user.html", context)
    else:
        context['filter_form'] = SubjectFilterForm(years=4)
        return render(request, "subjects.html", context)
