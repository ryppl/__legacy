"""distutils

The main package for the Python Module Distribution Utilities.  Normally
used from a setup script as

   from distutils.core import setup

   setup (...)
"""
__all__ = ['__version__', 'setup']

__revision__ = "$Id: __init__.py 78020 2010-02-06 16:37:32Z benjamin.peterson $"
__version__ = "1.0a1"

from distutils2.core import setup

