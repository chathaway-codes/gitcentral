from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from twisted.cred import portal
from twisted.conch.checkers import SSHPublicKeyChecker
from twisted.internet import reactor

from gitcentral.git_server import DjangoSSHKeyDB, GitRealm, GitSSHFactory

class Command(BaseCommand):
    def handle(self, *args, **options):
	p = portal.Portal(GitRealm())
	sshDB = SSHPublicKeyChecker(DjangoSSHKeyDB())
	p.registerChecker(sshDB)
	GitSSHFactory.portal = p

	reactor.listenTCP(settings.GIT_SERVER_PORT, GitSSHFactory())
	reactor.run()
