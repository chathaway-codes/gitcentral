from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.views.generic import ListView, DetailView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from .models import *

def check_permissions(repo, request, require_admin=False):
    """ Determines if the current user (in request) has permission to access repo
    Raises an exception if they cannot; so do not worry!
    """
    if require_admin:
        if request.user.is_authenticated() and repo.user_can_admin(request.user):
            return repo
        raise PermissionDenied()

    if request.method == "GET" and repo.public:
        return repo

    if not request.user.is_authenticated() \
            and repo.public == False:
        raise Http404
    if repo.owner == request.user:
        return repo

    permission = get_object_or_404(RepoPermission, repo=repo, owner=request.user)
    if request.method == "GET" and repo.user_can_read(request.user):
        return repo
    if (request.method == "POST" or request.method == "PUT") \
            and repo.user_can_write(request.user):
        return repo
    raise PermissionDenied()

class RepoDetailView(DetailView):
    model = Repo

    def returns_file(self):
        r = self.get_object().git_repo()
	if len(r.heads) == 0:
	    self.trees = []
	    self.blobs = []
	    class T:
	        path = ""
	    self.current_tree = T()
	    return False
        tree = r.heads.master.commit.tree
        trees = []
        ttree = tree
        path = self.kwargs['dirfile']
        if path != "":
            for p in path.split("/"):
		if p == "":
                    break
                found = False
                for t in ttree.trees:
                    if t.name == p:
                        ttree = t
                        found = True
                        break
                if not found:
                   # Must be a file; get it and return it
                   self.return_file = True
                   self.blob = ttree[p]
                   return True
        for tree in ttree.trees:
            trees += [{
              "name": tree.name,
              "path": tree.path
            }]
        blobs = []
        for blob in ttree.blobs:
            blobs += [{
              "name": blob.name,
              "path": blob.path
            }]
	self.blobs = blobs
	self.trees = trees
	self.current_tree = ttree
	return False

    def get(self, request, *args, **kwargs):
        if self.returns_file():
	    response = HttpResponse(content_type='application/octet-stream')
	    response['Content-Disposition'] = 'attachment; filename="%s"' % self.blob.name
	    response.write(self.blob.data_stream.read())
	    return response
	return super(RepoDetailView,self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RepoDetailView, self).get_context_data(**kwargs)
	self.return_file = False
        context['files'] = self.blobs
        context['dirs'] = self.trees
	context['can_admin'] = context['object'].user_can_admin(self.request.user)
	breadcrumbs = []
	current_path = ""
	for p in self.current_tree.path.split("/"):
	    if p == "":
	        continue
	    current_path = os.path.join(current_path, p)
	    breadcrumbs += [{
	        "name": p,
		"path": current_path
	    }]
	context['breadcrumbs'] = breadcrumbs
        return context

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        repo = get_object_or_404(Repo, owner=user, path=self.kwargs["path"])
	check_permissions(repo, self.request)
        return repo

class AllRepoListView(ListView):
    model = Repo

    def get_queryset(self):
	if self.request.user.is_authenticated():
		permissions = RepoPermission.objects.filter(owner=self.request.user)
		return Repo.objects.filter(Q(public=True) | Q(repopermission__in=permissions) | Q(owner=self.request.user)).distinct()
	return Repo.objects.filter(public=True)

class RepoListView(ListView):
    model = Repo

    def  get_context_data(self, **kwargs):
        context = super(RepoListView, self).get_context_data(**kwargs)
	context['repo_user'] = get_object_or_404(User, username=self.kwargs['username'])
	return context

    def get_queryset(self):
        owner=get_object_or_404(User, username=self.kwargs['username'])
	permissions = RepoPermission.objects.filter(owner=owner)
	if self.request.user.is_authenticated():
	    return Repo.objects.filter(Q(public=True) | Q(repopermission__in=permissions), Q(owner=owner)).distinct()
	return Repo.objects.filter(public=True, owner=owner)

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
        repo=get_object_or_404(Repo, pk=self.kwargs['pk'])
	check_permissions(repo, self.request, True)
	return RepoPermission.objects.filter(repo=repo)

class RepoPermissionCreateView(CreateView):
    model = RepoPermission
    fields = ('owner', 'permission',)

    def get_form(self, form_class=None):
        repo=get_object_or_404(Repo, pk=self.kwargs['pk'])
	check_permissions(repo, self.request, True)
        return super(RepoPermissionCreateView, self).get_form(form_class)

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
        repo=get_object_or_404(Repo, pk=self.kwargs['repo_id'])
	check_permissions(repo, self.request, True)
    	repo_permission = get_object_or_404(RepoPermission, owner=get_object_or_404(User, pk=self.kwargs['user_id']), repo=repo)
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
