from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import UpdateView, CreateView, DeleteView

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
	if self.request.user.is_authenticated():
		permissions = RepoPermission.objects.filter(owner=self.request.user)
		return Repo.objects.filter(Q(public=True) | Q(repopermission__in=permissions)).distinct()
	return Repo.objects.filter(public=True)

class RepoListView(ListView):
    model = Repo

    def  get_context_data(self, **kwargs):
        context = super(RepoListView, self).get_context_data(**kwargs)
	context['repo_user'] = get_object_or_404(User, username=self.kwargs['username'])
	return context

    def get_queryset(self):
	permissions = RepoPermission.objects.filter(owner=get_object_or_404(User, username=self.kwargs['username']))
	if self.request.user.is_authenticated():
	    return Repo.objects.filter(Q(public=True) | Q(repopermission__in=permissions)).distinct()
	return Repo.objects.filter(public=True)

class RepoCreateView(CreateView):
    model = Repo
    fields = ('name', 'public',)
    def get_success_url(self):
        return reverse('repo-detail', kwargs={"path": self.object.path, "username": self.object.owner.username, "dirfile": ""})

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(RepoCreateView, self).form_valid(form)

class RepoPermissionListView(ListView):
    model = RepoPermission

    def get_context_data(self, **kwargs):
        context = super(RepoPermissionListView, self).get_context_data(**kwargs)
	context['repo'] = get_object_or_404(Repo, pk=self.kwargs['pk'])
	return context

    def get_queryset(self):
	return RepoPermission.objects.filter(repo=get_object_or_404(Repo, pk=self.kwargs['pk']))

class RepoPermissionCreateView(CreateView):
    model = RepoPermission
    fields = ('owner', 'permission',)

    def get_success_url(self):
        return reverse('permission-list', kwargs={"pk": self.object.repo.pk})

    def form_valid(self, form):
        form.instance.repo = get_object_or_404(Repo, pk=self.kwargs['pk'])
	if RepoPermission.objects.filter(repo=form.instance.repo, owner=form.instance.owner).count() != 0:
	    raise PermissionDenied()
        return super(RepoPermissionCreateView, self).form_valid(form)

class RepoPermissionDeleteView(DeleteView):
    model = RepoPermission
    def get_success_url(self):
        return reverse('permission-list', kwargs={"pk": self.object.repo.pk})
    def get_object(self):
    	repo_permission = get_object_or_404(RepoPermission, owner=get_object_or_404(User, pk=self.kwargs['user_id']), repo=get_object_or_404(Repo, pk=self.kwargs['repo_id']))
        return repo_permission

class KeyListView(ListView):
    model = Key

    def get_queryset(self):
	return Key.objects.filter(owner=self.request.user)

class KeyCreateView(CreateView):
    model = Key
    fields = ('key',)

    def get_success_url(self):
        return reverse('user-repo-list', kwargs={"username": self.object.owner.username})

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(KeyCreateView, self).form_valid(form)

class KeyDeleteView(DeleteView):
    model = Key
    def get_success_url(self):
        return reverse('user-repo-list', kwargs={"username": self.object.owner.username})
    def get_object(self):
    	key = get_object_or_404(Key, owner=self.request.user, pk=self.kwargs['pk'])
        return key
