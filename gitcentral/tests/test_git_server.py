from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.test import TestCase

from gitcentral.git_server import can_run_command
from gitcentral.models import Repo, RepoPermission

class GitServerTestCases(TestCase):
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

    def test_has_permission_to_read(self):
        # If this command raises an exception, the permissions don't work
        can_run_command(self.test_user, "git-upload-pack '/%s'" % self.repos[0].get_relative_path())

    def test_does_have_permission_to_read(self):
        # If this command raises an exception, the permissions don't work
	user = User.objects.create_user(username="my_user", password="password")
	permission = RepoPermission.objects.create(owner=user, repo=self.repos[1], permission=0)
        can_run_command(user, "git-upload-pack '/%s'" % self.repos[1].get_relative_path())

    def test_does_not_have_permission_to_read(self):
        # If this command raises an exception, the permissions don't work
	user = User.objects.create_user(username="my_user", password="password")
	error_raised = False
	try:
            can_run_command(user, "git-upload-pack '/%s'" % self.repos[1].get_relative_path())
	except PermissionDenied:
	    error_raised = True
	self.assertTrue(error_raised)

    def test_has_permission_to_write(self):
        # If this command raises an exception, the permissions don't work
        can_run_command(self.test_user, "git-receive-pack '/%s'" % self.repos[0].get_relative_path())

    def test_does_not_have_permission_to_write(self):
        # If this command raises an exception, the permissions don't work
	user = User.objects.create_user(username="my_user", password="password")
	error_raised = False
	try:
            can_run_command(user, "git-receive-pack '/%s'" % self.repos[1].get_relative_path())
	except PermissionDenied:
	    error_raised = True
	self.assertTrue(error_raised)

    def test_does_not_has_permission_to_read_not_write(self):
        # If this command raises an exception, the permissions don't work
	user = User.objects.create_user(username="my_user", password="password")
	permission = RepoPermission.objects.create(owner=user, repo=self.repos[1], permission=0)
	error_raised = False
	try:
            can_run_command(user, "git-receive-pack '/%s'" % self.repos[1].get_relative_path())
	except PermissionDenied:
	    error_raised = True
	self.assertTrue(error_raised)
