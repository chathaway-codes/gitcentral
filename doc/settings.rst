.. toctree::
   :maxdepth: 2

=============
Settings
=============

``SERVER_PUBLIC_KEY``
---------------------

Default: ``None`` (No default)

Defines the SSH public key the server should use.
As with the private key, this must be defined.

``SERVER_PRIVATE_KEY``
----------------------

Default: ``None`` (No default)

Defines the SSH private key the server should use.
As with the public key, this must be defined.

It is important to keep this key private; please do some research on SSH.

``GIT_SHELL_PATH``
------------------

Default: ``/usr/bin/git-shell``

The path to git-shell, which is the shell that SSH will be enclosed in.
Although I don't believe there is any risk of a command being sent to this shell, using it provides an additional layer of security.

``GIT_RECEIVE_PACK``
--------------------

Default: ``/usr/bin/git-receive-pack``

The path the git-recieve-pack binary.

``GIT_UPLOAD_PACK``
-------------------

Default: ``/usr/bin/git-upload-pack``

The path to the git-upload-pack binary.
