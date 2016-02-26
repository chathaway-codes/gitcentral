from __future__ import unicode_literals

import os

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify

import git

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

class Key(models.Model):
    key = models.TextField()
    owner = models.ForeignKey(AUTH_USER_MODEL)

class RepoPermission(models.Model):
    owner = models.ForeignKey(AUTH_USER_MODEL)
    repo = models.ForeignKey('gitcentral.Repo')

    permission = models.IntegerField(default=0)

class Repo(models.Model):
    name = models.CharField(max_length=255)
    # End part of path
    path = models.CharField(max_length=255)
    owner = models.ForeignKey(AUTH_USER_MODEL)
    public = models.BooleanField(default=True)

    def __unicode__(self):
	return "%s/%s" % (self.owner.username, self.name)

    def get_relative_path(self):
	return os.path.join(self.owner.username, self.path)

    def user_can_read(self, user):
	if self.public:
	    return True
	get_object_or_404(RepoPermission, owner=user, repo=self)
	return True

    @staticmethod
    def get_repo_path(repo):
	return os.path.join(settings.GIT_ROOT, repo.owner.username, repo.path)

@receiver(post_save, sender=Repo)
def repo_pre_save(sender, instance, created, raw, **kwargs):
    if created:
	# TODO: Check if the first path is already taken; if so, guess at one
	instance.path = slugify(instance.name)
	instance.save()

	# Init a Git repo
	r = git.Repo.init(Repo.get_repo_path(instance), bare=True)

	# Make sure the owner has permissions on the repo
	permission = RepoPermission(owner=instance.owner, repo=instance, permission=3)
