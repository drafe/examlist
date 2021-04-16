from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect

from .forms import UploadFileForm, SubjectFilterForm, SubjectFilterUserForm
from .models import AcademicPlan, Specialty, Group

from itertools import groupby

# Create your views here.


def home(request):
    return render(request, 'home.html')


def logout_request(request):
    logout(request)
    return redirect('home')


@login_required
def upload_file(request):
    context = {'upload': UploadFileForm()}
    if request.method == 'POST':
        upload_form = UploadFileForm(request.POST, request.FILES)
        upload_form.set_page(request.FILES['page'])
        if upload_form.is_valid():
            # todo: прочитать нужную страницу, распарсить данные,
            #  перекинуть все на станицу проверки пользователем
            pass
        else:
            context['upload'] = upload_form

    return render(request, 'upload.html', context)


def subjects_filter(request):
    try:
        spec = int(request.GET['specialty'])
        sem = int(request.GET['semester'])
    except:
        qs = None
    else:
        qs = AcademicPlan.objects.select_related('id_specialty', 'id_subject').all()
        qs = qs.filter(id_specialty=spec).filter(semester=sem).order_by('control')
        spec = Specialty.objects.select_related('id_faculty').get(id=request.GET['specialty'])
        context = {'subjects': qs,
                   'title': f"{spec.id_faculty} {spec} {request.GET['semester']} семестр",
                   }
        return context


def subjects_user_filter(request):
    try:
        spec = int(request.GET['specialty'])
        sem = int(request.GET['semester'])
        year = int(request.GET['year'])
    except:
        qs = None
    else:
        semesters = [i for i in range(1, AcademicPlan.MAX_SEMESTER+1) if i % 2 != sem]
        gr = Group.objects.select_related('id_specialty')\
            .filter(id_specialty=spec)\
            .filter(enter_year__range=(year-3, year))\
            .values('enter_year').annotate(count=Count('id'))

        qs = AcademicPlan.objects.select_related('id_specialty', 'id_subject')\
            .filter(id_specialty=spec)\
            .filter(semester__in=semesters)\
            .order_by('semester')

        s = {}
        for q in qs:
            if q.semester in s:
                s[q.semester].append(q)
            else:
                s[q.semester] = [q, ]

        subjects = [{'course': (i+1 // 2), 'subjects': s[i]} for i in s]
        for i, g in enumerate(gr):
            subjects[i]['groups'] = g['count']

        spec = Specialty.objects.select_related('id_faculty').get(id=request.GET['specialty'])
        sem = 'осенний' if int(request.GET['semester']) == 0 else 'весенний'
        context = {'subjects': subjects,
                   'title': f"{spec.id_faculty} {spec} : {year}-{year + 1} уч.год {sem} семестр"
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

