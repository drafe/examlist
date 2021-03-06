"""examlists URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from listsapp.views import (
    home, upload_file, subjects_filter_list, academ_difference_list, SubjectConflictView, PlanItemsCreateView,
    SendMessageView
)
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('upload/', upload_file, name='upload'),
    path('upload/items/', PlanItemsCreateView.as_view(), name='upload_items'),
    path('upload/conflicts/', SubjectConflictView.as_view(), name='upload_conflicts'),
    path('subjects/', subjects_filter_list, name='subjects'),
    path('academ/', academ_difference_list, name='academ'),
    path('message/', SendMessageView.as_view(), name='message')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)