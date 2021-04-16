from datetime import date

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UploadFileForm, SubjectFilterForm, SubjectFilterUserForm
from .functionality.upload import handle_uploaded_file, is_xlsx
# Create your views here.
from django.views import generic

from .models import AcademicPlan, Faculty, Specialty, Group


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
    except :
        qs = None
    else:
        if request.user.is_authenticated:
            gr = Group.objects.select_related('id_specialty')
            qs = AcademicPlan.objects.select_related('id_specialty', 'id_subject').all()
        else:
            qs = AcademicPlan.objects.select_related('id_specialty', 'id_subject').all()
            qs = qs.filter(id_specialty=spec).filter(semester=sem)
    return qs


def SubjectsFilterView(request):
    context = {}
    if request.GET:
        qs = subjects_filter(request)
        spec = Specialty.objects.select_related('id_faculty').get(id=request.GET['specialty'])
        context = {'subjects': qs, }
        if request.user.is_authenticated:
            year = int(request.GET['year'])
            sem = 'осенний' if int(request.GET['semester']) == 0 else 'весенний'
            context['title'] = f"{spec.id_faculty} {spec} : {year}-{year+1} уч.год {sem} семестр"
        else:
            context['title'] = f"{spec.id_faculty} {spec} {request.GET['semester']} семестр"

    if request.user.is_authenticated:
        context['filter_form'] = SubjectFilterUserForm()
    else:
        context['filter_form'] = SubjectFilterForm(years=4)

    return render(request, "subjects_guest.html", context)

