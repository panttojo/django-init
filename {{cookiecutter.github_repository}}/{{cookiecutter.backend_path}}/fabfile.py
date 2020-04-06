"""Fabric file for managing this project.

See: http://www.fabfile.org/
"""

# Standard Library
from contextlib import contextmanager as _contextmanager
from functools import partial
from os.path import dirname, isdir, join

# Third Party Stuff
import os
from fabric.api import env
from fabric.api import local as fabric_local
from fabric import api as fab

local = partial(fabric_local, shell='/bin/bash')


HERE = dirname(__file__)

# ==============================================================================
#  Settings
# ==============================================================================
env.project_name = "{{ cookiecutter.main_module }}"
env.apps_dir = join(HERE, env.project_name)
env.static_dir = join(env.apps_dir, "static")
env.virtualenv_dir = join(HERE, "venv")
env.requirements_file = join(HERE, "requirements/development.txt")
env.shell = "/bin/bash -l -i -c"


def init(vagrant=False):
    """Prepare a local machine for development."""

    install_requirements()
    add_pre_commit()
    if not os.getenv("CI", "False").lower() == "true":
        manage("migrate")
        print('---------------------------------------------------------------')
        print('Creating a super user...')
        manage("createsuperuser")


def install_requirements(file=env.requirements_file):
    """Install project dependencies."""
    verify_virtualenv()
    # activate virtualenv and install
    with virtualenv():
        local("pip install -r %s" % file)


def add_pre_commit():
    verify_virtualenv()
    # activate virtualenv and install pre-commit hooks
    with virtualenv():
        local("pre-commit install")


def shell():
    manage("shell_plus")


def test(options="--pdb --cov"):
    """Run tests locally. By Default, it runs the test using --ipdb.
    You can skip running it using --ipdb by running - `fab test:""`
    """
    with virtualenv():
        local("flake8 .")
        local("pytest %s" % options)


def serve(host="127.0.0.1:8000"):
    """Run local developerment server, making sure that dependencies and
    database migrations are upto date.
    """
    install_requirements()
    migrate()
    manage("runserver %s" % host)


def makemigrations(app=""):
    """Create new database migration for an app."""
    manage("makemigrations %s" % app)


def migrate():
    """Apply database migrations."""
    manage("migrate")


def createapp(appname):
    """fab createapp:<appname>
    """
    path = join(env.apps_dir, appname)
    local("mkdir %s" % path)
    manage("startapp %s %s" % (appname, path))


# Helpers
# ------------------------------------------------------------------------------
def manage(cmd, venv=True):
    with virtualenv():
        local("python manage.py %s" % cmd)


@_contextmanager
def virtualenv():
    """Activates virtualenv context for other commands to run inside it.
    """
    with fab.cd(HERE):
        with fab.prefix("source %(virtualenv_dir)s/bin/activate" % env):
            yield


def verify_virtualenv():
    """This modules check and install virtualenv if it not present.
    It also creates local virtualenv directory if it's not present
    """
    from distutils import spawn

    if not spawn.find_executable("virtualenv"):
        local("sudo pip install virtualenv")

    if not isdir(env.virtualenv_dir):
        local("virtualenv %(virtualenv_dir)s -p $(which python3)" % env)


def precommit():
    with virtualenv():
        local("pre-commit run --all-files")
