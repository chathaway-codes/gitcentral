from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from gitcentral.models import Repo, RepoPermission

class RepoModelTestCases(TestCase):
    def setUp(self):
        self.test_user = User(username="charles")
	self.test_user.save()
    def test_can_get_path_for_repo(self):
        """Tests that get_repo_path returns a path which starts with GIT_REPO
	"""
	repo = Repo(name="This is my test repo", owner=self.test_user)
	repo.save()

	path = Repo.get_repo_path(repo)
	self.assertTrue(path.startswith(settings.GIT_ROOT))
    def test_can_get_string_representation(self):
    	"""Calls str(repo) and expects a return like <username>/<Repo name with not slug>
	"""
	repo = Repo(name="This is my test repo", owner=self.test_user)
	repo.save()

	name = str(repo)
	self.assertEqual(name, "charles/This is my test repo")

    def test_can_get_path(self):
    	"""Calls repo.get_relative_path and expects <username>/<repo-name-with-sluggify>
	"""
	repo = Repo(name="This is my test repo", owner=self.test_user)
	repo.save()

	name = repo.get_relative_path()
	self.assertEqual(name, "charles/this-is-my-test-repo")

    def test_user_can_not_read_repo(self):
        """Verifies that a user cannot read a non-public repo without permission
	"""
	test_user2 = User(username="Jim")
	test_user2.save()
	repo = Repo(name="This is my test repo", owner=self.test_user, public=False)

	self.assertFalse(repo.user_can_read(test_user2))

    def test_user_can_read_repo(self):
        """Verifies that a user can read a non-public repo with permission
	"""
	test_user2 = User(username="Jim")
	test_user2.save()
	repo = Repo(name="This is my test repo", owner=self.test_user, public=False)
	repo.save()

	RepoPermission(owner=test_user2, repo=repo).save()

	self.assertTrue(repo.user_can_read(test_user2))

    def test_user_can_not_write_repo(self):
        """Verifies that a user cannot write a non-public repo without permission
	"""
	test_user2 = User(username="Jim")
	test_user2.save()
	repo = Repo(name="This is my test repo", owner=self.test_user, public=False)

	self.assertFalse(repo.user_can_write(test_user2))

    def test_user_can_write_repo(self):
        """Verifies that a user can write a non-public repo with permission
	"""
	test_user2 = User(username="Jim")
	test_user2.save()
	repo = Repo(name="This is my test repo", owner=self.test_user, public=False)
	repo.save()

	RepoPermission(owner=test_user2, repo=repo, permission=2).save()

	self.assertTrue(repo.user_can_write(test_user2))
