from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView

from .models import *

class RepoDetailView(DetailView):
	model = Repo

	def get_object(self):
	    user = get_object_or_404(User, username=self.kwargs["username"])
	    repo = get_object_or_404(Repo, owner=user, path=self.kwargs["path"])
	    repo.user_can_read(self.request.user)
	    return repo

class AllRepoListView(ListView):
    model = Repo

    def get_queryset(self):
	permissions = RepoPermission.objects.filter(owner=self.request.user)
	return Repo.objects.filter(Q(public=True) | Q(repopermission__in=permissions))

class RepoListView(ListView):
    model = Repo

    def get_queryset(self):
	permissions = RepoPermission.objects.filter(owner=self.request.user)
	return Repo.objects.filter(Q(owner=self.request.user), Q(public=True) | Q(repopermission__in=permissions))

class RepoCreateView(CreateView):
    model = Repo
    fields = ('name', 'public',)
    def get_success_url(self):
        return reverse('repo-detail', kwargs={"path": self.object.path, "username": self.object.owner.username, "dirfile": ""})

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(RepoCreateView, self).form_valid(form)

