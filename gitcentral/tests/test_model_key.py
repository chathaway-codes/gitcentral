from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from gitcentral.models import Key

class RepoModelTestCases(TestCase):
    def setUp(self):
        self.test_user = User(username="charles")
	self.test_user.save()
    def test_can_create_key_with_comment(self):
        """Tests the ability to save and get a string for a key
	"""
	start_keys = Key.objects.count()
	key = Key.objects.create(key="ssh-rsa sadklfjioqwrutor349876jghhoqno3845q my_key", owner=self.test_user)
	self.assertEquals(str(key), "ssh-rsa sadklfjioq... my_key")
	self.assertEquals(start_keys+1, Key.objects.count())

    def test_can_create_key_without_comment(self):
        """Tests the ability to save and get a string for a key
	"""
	start_keys = Key.objects.count()
	key = Key.objects.create(key="ssh-rsa sadklfjioqwrutor349876jghhoqno3845q", owner=self.test_user)
	self.assertEquals(str(key), "ssh-rsa sadklfjioq...")
