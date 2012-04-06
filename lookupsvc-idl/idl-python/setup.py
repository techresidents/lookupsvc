#!/usr/bin/env python

from distutils.core import setup

setup(name='trlookupsvc',
      version='${project.version}',
      description='30and30 Service',
      packages=['trlookupsvc',
                'trlookupsvc.gen']
    )

