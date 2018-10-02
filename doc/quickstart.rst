.. toctree::
   :maxdepth: 2

=============
Quick Start
=============

**********************
Using as a new project
**********************

The following documents how to install Gitcentral in a stand-alone development environment.

If you are preparing for deployment, you should change the database (see https://docs.djangoproject.com/en/1.9/ref/databases/ for more information).


Install the system packages
===========================

::

    sudo apt-get install python-virtualenv
    sudo apt-get build-dep python-twisted

These commands will install python-virtualenv, which allows us to use Python virtual environments for development, 
and the build dependencies for python-twisted, which is used to contruct the restricted SSH server that is used to share Git repos.

Strictly speaking, you do not need python-virtualenv.
However, it helps keep the build environment clean from interactions with other projects, which sometimes causes unforeseen problems.

Install local packages
======================

If you are using the suggested system, simply run::

    . ./activate

This will create a python virtual environment. Download, build, and install all required packages.

If you are not using the suggested system, you can install the packages using pip by running::

    pip install -r libraries.txt

Setup the SSH keys
==================

Gitcentral uses SSH to allow users to authenticate and clone repositories over an internet connection.
SSH is used because it has several well-supported technology stacks, and is more secure than HTTP.
For the server to provide SSH, it needs to be configured with a SSH private key and a SSH public key.
These keys are used in conjunction to form an asymmetric encryption scheme that provides the added ability for clients to authenticate the server.
To setup these keys, do the following::

    ssh-keygen -t rsa -f id_rsa -N ''
    # The following commenads copy the keys into the configuration file
    echo -n 'SERVER_PUBLIC_KEY = """' > local_settings.py
    cat id_rsa.pub >> local_settings.py
    echo -n -e "\"\"\"\n\nSERVER_PRIVATE_KEY = \"\"\"" >> local_settings.py
    cat id_rsa >> local_settings.py
    echo -e "\"\"\"" >> local_settings.py

Take special note of the local_settings.py file.
This file contains the configuration options that you specify, which should override the default.
More information on this will be provided later.

Setup the database
==================

The last step before running is to set up the database.
This section does not cover using a database other than SQLite, which is documented in the Django documentation (https://docs.djangoproject.com/en/1.9/ref/settings/#databases).::

    python manage.py migrate
    python manage.py createsuperuser

And you're off!

The second command launches a script which creates a super user who will have access to the backend (http://localhost:8000/admin) in addition to the front end.
Although this user shouldn't be needed, it is not a bad idea to have him as a backup.

Running the server
==================

The last step is to make sure everything is set up right, and run the server.
First, we will make sure all the tests pass.
This should provide good proof that everything is working.::

    python manage.py test

If the tests pass, we can run the server with::

    python manage.py runserver

And in a seperate terminal, launch the SSH server::

    python manage.py git_server

**********************************
A few notes for production servers
**********************************

local_settings.py
=================

This file should exist in the root of the Git repository, and contains all settings that shouldn't be stored in source control, such as:

* The secret key (which used to verify client-side cookies haven't been altered)
* The SSH key
* The database settings, including password
* Override to DEBUG

At the minimum, your local_settings.py file should have::

    SERVER_PUBLIC_KEY = """MY SSH KEY
    """

    SERVER_PRIVATE_KEY = """MY SSH PRIVATE KEY
    """

    SECRET_KEY = "my top secret key that you have changed"
    DEBUG = False

If you get "access denied" messages, also try setting ALLOWED_HOSTS (https://docs.djangoproject.com/en/1.9/ref/settings/#allowed-hosts)

Providing access to multiple clients
====================================

First and foremost; this is a complex topic, and we don't cover it in detail here.
You should not use the Django runserver command in a production environment; instead see https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/modwsgi/

If you don't want to listen to me and intend to host using the runserver command, use this::

    python manage.py runserver 0.0.0.0:8000


