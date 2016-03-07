
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from gitcentral.models import Key
from gitcentral.views import KeyCreateView, KeyDeleteView, KeyListView

class KeyViewTestCases(TestCase):
    @classmethod
    def setUpTestData(cls):
	cls.test_user = User.objects.create_user(username="testuser", password="password")
        cls.repos = [
	    Key.objects.create(owner=cls.test_user, key="key123"),
	    Key.objects.create(owner=cls.test_user, key="key456"),
	]

    def test_key_list_view(self):
        self.assertTrue(self.client.login(username=self.test_user.username, password="password"))
        self.client.get(reverse('key-list'))
	self.client.logout()

    def test_repo_list_all_view(self):
        self.client.get(reverse('repo-list'))

    def test_repo_create_view(self):
        self.assertTrue(self.client.login(username=self.test_user.username, password="password"))
	initialKeys = Key.objects.count()
        response = self.client.post(reverse('key-create'), {
	    "owner": "Alphabet soup",
	    "key": "Hello world!"
	})
	self.assertEqual(response.status_code, 302)
	self.assertTrue(initialKeys + 1 == Key.objects.count())
	self.client.logout()

    def test_repo_delete_view(self):
        self.assertTrue(self.client.login(username=self.test_user.username, password="password"))
	initialKeys = Key.objects.count()
        response = self.client.post(reverse('key-create'), {
	    "owner": "Alphabet soup",
	    "key": "Hello world!"
	})
	self.assertEqual(response.status_code, 302)
	respone = self.client.delete(reverse('key-delete', kwargs={'pk': self.test_user.key_set.all()[0].pk}))
	self.assertEqual(response.status_code, 302)
	self.assertTrue(initialKeys == Key.objects.count())
	self.client.logout()
