"""ryppl.core

The only module that needs to be imported to use the Distutils; provides
the 'setup' function (which is to be called from the setup script).  Also
indirectly provides the Distribution and Command classes, although they are
really defined in ryppl.dist and ryppl.cmd.
"""

__revision__ = "$Id: core.py 77704 2010-01-23 09:23:15Z tarek.ziade $"

import sys
import os
distutils2.core import *
from ryppl.dist import Distribution

import distutils2.core


def setup(**attrs):
    # Determine the distribution class -- either caller-supplied or
    # our Distribution (see below).
    klass = attrs.get('distclass')
    if klass:
        del attrs['distclass']
    else:
        klass = Distribution

    return distutils2.core.setup(distclass = klass, **attrs)
