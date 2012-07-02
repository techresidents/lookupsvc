#!/usr/bin/env python

from distutils.core import setup

setup(name='trlookupsvc',
      version='${project.version}',
      description='Tech Residents Service',
      packages=['trlookupsvc',
                'trlookupsvc.gen']
    )

