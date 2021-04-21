from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.forms import formset_factory, BaseFormSet
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from .forms import UploadFileForm, SubjectFilterForm, SubjectFilterUserForm, PlanItemUpload, SubjectConflictSolve
from .functionality.comparison import FuzzySubjectsComparison, AcademicDifferenceComparison
from .functionality.parser import Parser

from .models import AcademicPlan, Specialty, Group, Subject


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
    PlanItemsFormSet = formset_factory(PlanItemUpload)

    @staticmethod
    def init_item(subj, item):
        subject = Subject.objects.get(id=subj[item[0]])
        return dict(id_subject=subj[item[0]],
                    subject=subject.subject,
                    semester=item[1],
                    h_lecture=item[2],
                    h_laboratory=item[3],
                    h_practice=item[4],
                    control=item[5])

    def init_forms(self, request):
        request.session['row_data'] = self.row_data
        subj = self.row_data.get('subjects')
        data = [_ + [AcademicPlan.EXAM] for _ in self.row_data.get('exam')] + \
               [_ + [AcademicPlan.QUIZ] for _ in self.row_data.get('quiz')] + \
               [_ + [AcademicPlan.M_QU] for _ in self.row_data.get('m_qu')]
        data = sorted(data, key=lambda x: x[0])
        init = [self.init_item(subj, e) for e in data]
        return init

    def get(self, request):

        self.row_data = request.session.pop("row_data", None)
        if self.row_data is None:
            raise Http404('')

        init = self.init_forms(request)
        formset = self.PlanItemsFormSet(initial=init)
        formset.forms = formset.initial_forms

        return render(request, self.template_name, {'plan_formset': formset})

    def post(self, request):
        self.row_data = request.session.pop("row_data", None)
        if self.row_data is None:
            raise Http404('')

        init = self.init_forms(request)
        formset = self.PlanItemsFormSet(request.POST, initial=init)
        formset.forms = formset.initial_forms
        request.session['row_data'] = self.row_data

        if formset.is_valid():
            faculty = self.row_data.get('faculty')
            degree = self.row_data.get('degree')
            spec = Specialty(id_faculty_id=faculty, id_degree_id=degree, specialty=self.row_data.get('specialty'))
            spec.save()
            for form in formset:
                form.cleaned_data.pop('subject')
                form.cleaned_data['id_specialty'] = spec
                form.cleaned_data['id_subject_id'] = form.cleaned_data.pop('id_subject')
                plan = AcademicPlan(**form.cleaned_data)
                plan.save()
            return redirect('home')

        context = dict(plan_formset=formset)
        return render(request, self.template_name, context)


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
            row_data['degree'] = upload_form.cleaned_data['degree'].id

            request.session['row_data'] = row_data
            request.session['key'] = True
            return redirect('upload_conflicts')
        else:
            context['upload'] = upload_form

    return render(request, 'upload_file.html', context)


def subjects_filter(request):
    try:
        sp = request.GET.get('specialty')
        sem = request.GET.get('semester')
    except:
        return None
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
        spec = int(request.GET['specialty'])
        sem = int(request.GET['semester'])
        year = int(request.GET['year'])
    except:
        return None
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

        subjects = [{'course': ((i + 1) // 2), 'subjects': s[i]} for i in s]
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


def subjects_filter_list(request):
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


def academ_difference_list(request):
    context = dict(from_specialty=SubjectFilterForm(prefix='from', years=4),
                   to_specialty=SubjectFilterForm(prefix='to', years=4))

    if request.GET:
        from_specialty = SubjectFilterForm(request.GET, prefix='from', years=4)
        to_specialty = SubjectFilterForm(request.GET, prefix='to', years=4)
        if from_specialty.is_valid() and to_specialty.is_valid():
            title = f"{from_specialty.cleaned_data['specialty']} ({from_specialty.cleaned_data['semester']} семестр) -> " \
                    f"{to_specialty.cleaned_data['specialty']} ({to_specialty.cleaned_data['semester']} семестр) "
            difference_info = AcademicDifferenceComparison(
                from_specialty=from_specialty.cleaned_data['specialty'],
                from_semester=from_specialty.cleaned_data['semester'],
                to_specialty=to_specialty.cleaned_data['specialty'],
                to_semester=to_specialty.cleaned_data['semester']
            ).compare()
            context = dict(from_specialty=from_specialty,
                           to_specialty=to_specialty,
                           difference=difference_info,
                           title=title)

    return render(request, 'academ_ask.html', context)
