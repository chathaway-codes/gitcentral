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

    def test_permission_list_view_denied(self):
        response = self.client.get(reverse('permission-list', kwargs={"pk": self.repos[0].pk}))
	self.assertEqual(403, response.status_code)

    def test_permission_list_view(self):
	self.client.login(username=self.test_user.username, password="password")
        response = self.client.get(reverse('permission-list', kwargs={"pk": self.repos[0].pk}))
	self.assertEqual(200, response.status_code)
	self.client.logout()

    def test_permission_create_view_denied(self):
        response = self.client.get(reverse('permission-create', kwargs={"pk": self.repos[0].pk}))
	self.assertEqual(403, response.status_code)

    def test_permission_create_get_view(self):
	self.client.login(username=self.test_user.username, password="password")
        response = self.client.get(reverse('permission-create', kwargs={"pk": self.repos[0].pk}))
	self.assertEqual(200, response.status_code)
	self.client.logout()

    def test_permission_create_view(self):
	self.client.login(username=self.test_user.username, password="password")
	user = User.objects.create_user(username="this_test_user", password="abc")
        response = self.client.post(reverse('permission-create', kwargs={"pk": self.repos[0].pk}), {
	    "owner": user.pk,
	    "permission": 2
	})
	self.assertEqual(302, response.status_code)
	self.client.logout()

    def test_permission_create_view_duplicate_user(self):
	self.client.login(username=self.test_user.username, password="password")
        response = self.client.post(reverse('permission-create', kwargs={"pk": self.repos[0].pk}), {
	    "owner": 1,
	    "permission": 2
	})
	self.assertEqual(403, response.status_code)
	self.client.logout()

    def test_permission_delete_view(self):
	self.client.login(username=self.test_user.username, password="password")
        response = self.client.delete(reverse('permission-delete', kwargs={
	    "user_id": 1,
	    "repo_id": self.repos[0].pk
	}))
	self.assertEqual(302, response.status_code)
	self.client.logout()
