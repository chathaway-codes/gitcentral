from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from gitcentral.models import Repo, RepoPermission
from gitcentral.views import AllRepoListView, RepoCreateView, RepoDetailView, RepoListView

class RepoViewTestCases(TestCase):
    @classmethod
    def setUpTestData(cls):
	cls.test_user = User.objects.create_user(username="testuser", password="password")
        cls.repos = [
	    Repo.objects.create(name="This is my test repo", owner=cls.test_user),
	    Repo.objects.create(name="This is my private repo", owner=cls.test_user, public=False),
	]

    def test_repo_detail_view(self):
        self.client.get(reverse('repo-detail', kwargs={
	    "username": self.repos[0].owner.username, "path": self.repos[0].path,"dirfile": ""}))

    def test_repo_list_view(self):
        self.client.get(reverse('user-repo-list', kwargs={
	    "username": self.repos[0].owner.username}))

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
