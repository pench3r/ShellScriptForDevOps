#!/usr/bin/python
# encoding: utf-8
# -*- coding: utf8 -*-
"""
Created by PyCharm.
File:               LinuxBashShellScriptForOps:pyFabricAndCapistrano.py
User:               Liuhongda
Create Date:        2017/9/12
Create Time:        13:48
Description:        python script for automatic deploy using Fabric and Capistrano structure
References:         https://github.com/dlapiduz/fabistrano
                    http://www.fabfile.org/
                    http://capistranorb.com/documentation/getting-started/structure/#
Prerequisites:      fabric
 """
import functools
import re
import sys

import time
from fabric.api import run, env, sudo, task
from fabric.colors import *
from fabric.operations import require

env.interactive_mode = True
env.roledefs = {
    "develop": [
        "root@23.83.243.40"
    ],

    "sit": ['10.45.51.99',
            '10.46.68.233',
            '10.47.49.161',
            '10.46.69.219',
            ],
    "uat": [],
    "prod": ["10.160.46.5",
             "10.160.8.189",
             "10.25.0.93",
             "10.24.232.132",
             "10.171.168.179",
             "10.172.200.22",
             "10.132.10.244",
             "10.132.5.122",
             "10.132.4.168",
             "10.132.1.123",
             "10.132.0.59",
             "10.132.10.208",
             "10.47.50.145",
             "10.47.162.31",
             ],
}

env.roledefs["all"] = [host for role in env.roledefs.values() for host in role]

STAGES = {
    'develop': {
        'port': 26954,
        'user': 'root',
        'key_filename': r'c:\Users\Guodong\.ssh\exportedkey201310171355',
        'base_dir': '/var/www',
        'app_name': "kissops",
        'deploy_to': '/var/www/kissops',  # Note: this is not used, for human readable purpose
        "scm": 'git',
        "repo_url": 'https://github.com/DingGuodong/kissops.git',
        'git_branch': 'master',
        'packages_install': 'libmysqlclient-dev',  # TODO
        'restart_cmd': "/etc/init.d/kissops restart",
        "log_level": 'debug',
        "keep_releases": 10
        # ...
    },
    'production': {
        'hosts': ['breyten@example.org'],
        'code_dir': '/var/www/example.org',
        'code_branch': 'production',
        # ...
    },
}

env.skip_bad_hosts = True
env.remote_interrupt = True

env.timeout = 6000


def stage_set(stage_name='develop'):
    env.stage = stage_name
    for option, value in STAGES[env.stage].items():
        setattr(env, option, value)


@task
def develop():
    stage_set('develop')


@task
def prod():
    stage_set('prod')


def dir_exists(path):
    return run('[ -d %s ] && echo 0 || echo 1' % path) == '0'


def with_defaults(func):
    """A decorator that sets all defaults for a task."""

    @functools.wraps(func)
    def decorated(*args, **kwargs):
        env.setdefault('use_sudo', True)
        env.setdefault('python_bin', 'python')
        env.setdefault('remote_owner', 'www-data')
        env.setdefault('remote_group', 'www-data')
        env.setdefault('pip_install_command', 'pip install -r requirements.txt')
        env.setdefault('domain_path', "%(base_dir)s/%(app_name)s" %
                       {'base_dir': env.base_dir,
                        'app_name': env.app_name})
        env.setdefault('current_path', "%(domain_path)s/current" %
                       {'domain_path': env.domain_path})
        env.setdefault('releases_path', "%(domain_path)s/releases" %
                       {'domain_path': env.domain_path})
        env.setdefault('shared_path', "%(domain_path)s/shared" %
                       {'domain_path': env.domain_path})
        if 'releases' not in env.keys():
            if dir_exists(env.releases_path):
                env.releases = sorted(run('ls -x %(releases_path)s' % {'releases_path': env.releases_path}).split())

                if len(env.releases) >= 1:
                    env.current_revision = env.releases[-1]
                    env.current_release = "%(releases_path)s/%(current_revision)s" % \
                                          {'releases_path': env.releases_path,
                                           'current_revision': env.current_revision}
                if len(env.releases) > 1:
                    env.previous_revision = env.releases[-2]
                    env.previous_release = "%(releases_path)s/%(previous_revision)s" % \
                                           {'releases_path': env.releases_path,
                                            'previous_revision': env.previous_revision}
            else:
                env.releases = []

        return func(*args, **kwargs)

    return decorated


def sudo_run(*args, **kwargs):
    if env.use_sudo and env.user != 'root':
        sudo(*args, **kwargs)
    else:
        run(*args, **kwargs)


@task
@with_defaults
def restart():
    """Restarts your application"""
    try:
        run("touch %(current_release)s/%(wsgi_path)s" %
            {'current_release': env.current_release,
             'wsgi_path': env.wsgi_path})
    except AttributeError:
        try:
            sudo_run(env.restart_cmd)
        except AttributeError:
            pass


@with_defaults
def permissions():
    """Make the release group-writable"""
    sudo_run("chown -R %(user)s:%(group)s %(domain_path)s" %
             {'domain_path': env.domain_path,
              'user': env.remote_owner,
              'group': env.remote_group})
    sudo_run("chmod -R g+w %(domain_path)s" % {'domain_path': env.domain_path})


@task
@with_defaults
def setup():
    """Prepares one or more servers for deployment"""
    sudo_run("mkdir -p %(domain_path)s/{releases,shared}" % {'domain_path': env.domain_path})
    sudo_run("mkdir -p %(shared_path)s/{system,log,data,conf}" % {'shared_path': env.shared_path})
    permissions()


@with_defaults
def checkout():
    """Checkout code to the remote servers"""
    current_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    env.current_release = "%(releases_path)s/%(time)s" % {'releases_path': env.releases_path, 'time': current_time}
    run("cd %(releases_path)s; git clone -b %(git_branch)s -q %(git_clone)s %(current_release)s" %
        {'releases_path': env.releases_path,
         'git_clone': env.repo_url,
         'current_release': env.current_release,
         'git_branch': env.git_branch})


@task
def update():
    """Copies your project and updates environment and symlink"""
    update_code()
    update_env()
    symlink()
    set_current()
    permissions()


@task
def update_code():
    """Copies your project to the remote servers"""
    checkout()
    permissions()


@with_defaults
def symlink():
    """Updates the symlink to the most recently deployed version"""
    run("ln -nfs %(shared_path)s/log %(current_release)s/log" % {'shared_path': env.shared_path,
                                                                 'current_release': env.current_release})


@with_defaults
def set_current():
    """Sets the current directory to the new release"""
    run("ln -nfs %(current_release)s %(current_path)s" % {'current_release': env.current_release,
                                                          'current_path': env.current_path})


@with_defaults
def update_env():
    """Update servers environment on the remote servers"""
    sudo_run("cd %(current_release)s; %(pip_install_command)s" % {'current_release': env.current_release,
                                                                  'pip_install_command': env.pip_install_command})
    permissions()


@task
@with_defaults
def cleanup():
    """Clean up old releases"""
    if len(env.releases) > 3:
        directories = env.releases
        directories.reverse()
        del directories[:3]
        env.directories = ' '.join(
            ["%(releases_path)s/%(release)s" % {'releases_path': env.releases_path, 'release': release} for release in
             directories])
        run("rm -rf %(directories)s" % {'directories': env.directories})


@with_defaults
def rollback_code():
    """Rolls back to the previously deployed version"""
    if len(env.releases) >= 2:
        env.current_release = env.releases[-1]
        env.previous_revision = env.releases[-2]
        env.current_release = "%(releases_path)s/%(current_revision)s" % {'releases_path': env.releases_path,
                                                                          'current_revision': env.current_revision}
        env.previous_release = "%(releases_path)s/%(previous_revision)s" % {'releases_path': env.releases_path,
                                                                            'previous_revision': env.previous_revision}
        run("rm %(current_path)s; ln -s %(previous_release)s %(current_path)s && rm -rf %(current_release)s" % {
            'current_release': env.current_release, 'previous_release': env.previous_release,
            'current_path': env.current_path})


@task
def rollback():
    """Rolls back to a previous version and restarts"""
    rollback_code()
    permissions()
    restart()


def before_deploy():
    """check env, upload files, execute shell script(such as add user, install essential packages)"""
    pass


def after_deploy():
    """ mail to admin, etc"""
    pass


@task(default=True)
def deploy():
    """Deploys your project. This calls both `update' and `restart'"""
    require('stage', provided_by=(develop,))  # make sure 'develop' env stage is set
    before_deploy()
    setup()
    update()
    restart()
    after_deploy()


@task
def connectivity_test():
    stage_set('develop')
    run("uname -a")


def terminal_debug(fabric_task):
    command = "fab -i {ssh_key_filename} -f {fab_file} -R {roles} {task}".format(ssh_key_filename=env.key_filename,
                                                                                 roles="develop",
                                                                                 fab_file=__file__,
                                                                                 task=fabric_task)
    print command
    sys.exit(os.system(command))


def is_windows():
    return True if 'nt' in sys.builtin_module_names else False


def is_linux():
    # Note: not validate on Mac OSX
    return True if 'posix' in sys.builtin_module_names else False


if __name__ == '__main__':
    if len(sys.argv) == 1 and is_windows():
        # terminal_debug("connectivity_test")
        terminal_debug("develop deploy")  # execute "deploy" task on "develop" stage hosts

    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    print red("Please use 'fab -f %s'" % " ".join(str(x) for x in sys.argv[0:]))
    sys.exit(1)
