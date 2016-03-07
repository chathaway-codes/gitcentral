from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from gitcentral.models import Repo, RepoPermission
from gitcentral.views import AllRepoListView, RepoCreateView, RepoDetailView, RepoListView

class RepoViewTestCases(TestCase):
    @classmethod
    def setUpTestData(cls):
	cls.test_user = User.objects.create_user(username="test_data", password="password")
        cls.repos = [
	    Repo.objects.create(name="This is my test repo", owner=cls.test_user),
	    Repo.objects.create(name="This is my private repo", owner=cls.test_user, public=False),
	    Repo.objects.create(name="This is my repo with commits", owner=cls.test_user),
	    Repo.objects.create(name="This is my private repo with commits", owner=cls.test_user),
	]

	cls.repos[2].path = "test_repo1"
	cls.repos[2].save()
	cls.repos[3].path = "test_repo2"
	cls.repos[3].save()

    def test_repo_detail_view(self):
        self.client.get(reverse('repo-detail', kwargs={
	    "username": self.repos[0].owner.username, "path": self.repos[0].path,"dirfile": ""}))

    def test_repo_detail_view_get_file(self):
        self.client.get(reverse('repo-detail', kwargs={
	    "username": self.repos[2].owner.username, "path": self.repos[2].path,"dirfile": "README.md"}))

    def test_repo_detail_view_show_folder(self):
        self.client.get(reverse('repo-detail', kwargs={
	    "username": self.repos[2].owner.username, "path": self.repos[2].path,"dirfile": "hello/world/"}))

    def test_repo_detail_view_get_file_in_folder(self):
        self.client.get(reverse('repo-detail', kwargs={
	    "username": self.repos[2].owner.username, "path": self.repos[2].path,"dirfile": "hello/world/secret.txt"}))

    def test_repo_detail_view_all_repos(self):
        for r in self.repos:
	    self.client.login(username=r.owner.username, password="password")
            response = self.client.get(reverse('repo-detail', kwargs={
	        "username": r.owner.username, "path": r.path,"dirfile": ""}))
	    self.assertEqual(response.status_code, 200)
	    self.client.logout()

    def test_repo_view_denied(self):
	response = self.client.get(reverse('repo-detail', kwargs={
	    'username': self.repos[1].owner.username, "path": self.repos[1].path, "dirfile": ""}))
	self.assertEqual(response.status_code, 404)

    def test_repo_view_with_login(self):
	r = self.repos[1]
	user = User.objects.create_user(username="my_user", password="hotdogs")
	RepoPermission.objects.create(owner=user, repo=r, permission=0)
	self.assertTrue(self.client.login(username=user.username, password="hotdogs"))
	response = self.client.get(reverse('repo-detail', kwargs={
	    'username': r.owner.username, "path": r.path, "dirfile": ""}))
	self.assertEqual(response.status_code, 200)
	self.client.logout()

    def test_repo_list_view(self):
        self.client.get(reverse('user-repo-list', kwargs={
	    "username": self.repos[0].owner.username}))

    def test_repo_list_view_with_login(self):
        self.assertTrue(self.client.login(username=self.test_user.username, password="password"))
        self.client.get(reverse('user-repo-list', kwargs={
	    "username": self.repos[0].owner.username}))
	self.client.logout()

    def test_repo_list_index_with_login(self):
        self.assertTrue(self.client.login(username=self.test_user.username, password="password"))
        self.client.get(reverse('repo-list'))
	self.client.logout()

    def test_repo_list_all_view(self):
        self.client.get(reverse('repo-list'))

    def test_repo_create_view(self):
        self.assertTrue(self.client.login(username=self.test_user.username, password="password"))
	initialRepos = Repo.objects.count()
        response = self.client.post(reverse('repo-create'), {
	    "name": "My awesome project",
	    "public": False
	})
	self.assertEqual(response.status_code, 302)
	self.assertTrue(initialRepos + 1 == Repo.objects.count())
	self.client.logout()

    def test_repo_admin_view(self):
        self.assertTrue(self.client.login(username=self.test_user.username, password="password"))
	response = self.client.get(reverse('permission-list', kwargs={'pk': self.repos[0].pk}))
	self.assertEqual(response.status_code, 200)
	self.client.logout()

    def test_repo_admin_view_denied(self):
	response = self.client.get(reverse('permission-list', kwargs={'pk': self.repos[0].pk}))
	self.assertEqual(response.status_code, 403)
