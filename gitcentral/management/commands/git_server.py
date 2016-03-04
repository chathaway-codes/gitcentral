import fcntl
import os
import pty
import socket
import struct
import sys
import time
import tty

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.http import HttpResponse

from twisted.cred import portal
from twisted.conch import avatar
from twisted.conch.unix import SSHSessionForUnixConchUser
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.conch.checkers import SSHPublicKeyChecker, InMemorySSHKeyDB
from twisted.conch.ssh import factory, userauth, connection, keys, session
from twisted.internet import reactor, protocol
from twisted.python import log, components
from zope.interface import implements

from gitcentral.models import Key, Repo

class GitAvatar(avatar.ConchUser):

    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session':session.SSHSession})

class GitRealm:
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        return interfaces[0], GitAvatar(avatarId), lambda: None

class GitSession(SSHSessionForUnixConchUser):
    def execCommand(self, proto, cmd):
        shell = '/usr/bin/git-shell'
	cmd, path = cmd.split(" ", 2)
	path = path.replace("'", "")
	path = path[1:]
	repo_username, path = path.split("/", 2)
	repo_owner = User.objects.get(username=repo_username)
	repo = Repo.objects.get(path=path, owner=repo_owner)
	if not repo.user_can_read(User.objects.get(username=self.avatar.username)):
	    raise PermissionDenied()
	# If the user is writing, verify they can
	if cmd == "git-receive-pack" and not repo.user_can_write(User.objects.get(username=self.avatar.username)):
		raise PermissionDenied()
	path = Repo.get_repo_path(repo)
        command = (cmd, path)
        peer = self.avatar.conn.transport.transport.getPeer()
        host = self.avatar.conn.transport.transport.getHost()
        if self.ptyTuple:
            self.getPtyOwnership()
        self.pty = self._reactor.spawnProcess(proto, cmd, command, usePTY=self.ptyTuple or 0)
        if self.ptyTuple:
            self.addUTMPEntry()
            if self.modes:
                self.setModes()
        self.avatar.conn.transport.transport.setTcpNoDelay(1)

    def openShell(self, proto):
	if not self.ptyTuple:  # We didn't get a pty-req.
	    log.msg('tried to get shell without pty, failing')
	    raise ConchError("no pty")
	shell = '/usr/bin/git-shell'
	self.getPtyOwnership()
	self.pty = self._reactor.spawnProcess(proto, shell, usePTY=self.ptyTuple)
	self.addUTMPEntry()
	fcntl.ioctl(self.pty.fileno(), tty.TIOCSWINSZ,
		struct.pack('4H', *self.winSize))
	if self.modes:
	    self.setModes()
	self.oldWrite = proto.transport.write
	proto.transport.write = self._writeHack
	self.avatar.conn.transport.transport.setTcpNoDelay(1)

class GitSSHFactory(factory.SSHFactory):
    publicKeys = {
        'ssh-rsa': keys.Key.fromString(data=settings.SERVER_PUBLIC_KEY)
    }
    privateKeys = {
        'ssh-rsa': keys.Key.fromString(data=settings.SERVER_PRIVATE_KEY)
    }
    services = {
        'ssh-userauth': userauth.SSHUserAuthServer,
        'ssh-connection': connection.SSHConnection
    }

class DjangoSSHKeyDB(object):
    def getAuthorizedKeys(self, username):
        k = Key.objects.filter(owner__username=username)
	return map(lambda a: keys.Key.fromString(data=a.key), k)

components.registerAdapter(GitSession, GitAvatar, session.ISession)

class Command(BaseCommand):
    def handle(self, *args, **options):
	p = portal.Portal(GitRealm())
	users = {}
	sshDB = SSHPublicKeyChecker(DjangoSSHKeyDB())
	p.registerChecker(sshDB)
	GitSSHFactory.portal = p

	reactor.listenTCP(settings.GIT_SERVER_PORT, GitSSHFactory())
	reactor.run()
