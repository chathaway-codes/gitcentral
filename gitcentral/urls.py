"""gitcentral URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from .views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^accounts/', include('allauth.urls')),

    url(r'^repo/$', AllRepoListView.as_view(), name="repo-list"),
    url(r'^repo/create/$', RepoCreateView.as_view(), name="repo-create"),
    url(r'^repo/(?P<username>\w+)/$', RepoListView.as_view(), name="user-repo-list"),
    url(r'^repo/(?P<username>\w+)/(?P<path>[\w-]+)/(?P<dirfile>.*)$', RepoDetailView.as_view(), name="repo-detail"),

    url(r'^permission/(?P<repo_id>\d+)/(?P<user_id>\d+)/delete$', RepoPermissionDeleteView.as_view(), name="permission-delete"),
    url(r'^permission/(?P<pk>\d+)/create/$', RepoPermissionCreateView.as_view(), name="permission-create"),
    url(r'^permission/(?P<pk>\d+)/$', RepoPermissionListView.as_view(), name="permission-list"),

    url(r'^key/(?P<pk>\d+)/delete$', KeyDeleteView.as_view(), name="key-delete"),
    url(r'^key/create/$', KeyCreateView.as_view(), name="key-create"),
    url(r'^key/$', KeyListView.as_view(), name="key-list"),
]
