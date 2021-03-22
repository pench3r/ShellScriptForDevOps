#!/usr/bin/python
# encoding: utf-8
# -*- coding: utf8 -*-
"""
Created by PyCharm.
File:               LinuxBashShellScriptForOps:pyFabricWithStages.py
User:               Liuhongda
Create Date:        2017/9/12
Create Time:        13:16
Description:        deploy service by Fabric with staging support.
References:         http://yerb.net/blog/2014/03/03/multiple-environments-for-deployment-using-fabric/
Prerequisites:      []
 """
from fabric.api import env, task
from fabric.operations import require

# from fabric.decorators import runs_once
# from fabric.context_managers import cd, lcd, settings, hide

STAGES = {
    'test': {
        'hosts': ['breyten@test.example.org'],
        'code_dir': '/var/www/test.example.org',
        'code_branch': 'master',
        # ...
    },
    'production': {
        'hosts': ['breyten@example.org'],
        'code_dir': '/var/www/example.org',
        'code_branch': 'production',
        # ...
    },
}


def stage_set(stage_name='test'):
    env.stage = stage_name
    for option, value in STAGES[env.stage].items():
        setattr(env, option, value)


@task
def production():
    stage_set('production')


@task
def test():
    stage_set('test')


@task
def deploy():
    """
    Deploy the project.
    """

    require('stage', provided_by=(test, production,))
    # ...
