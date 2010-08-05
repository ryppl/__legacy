import sys
from setuptools import setup, find_packages
import os

version = "0.1dev"

doc_dir = os.path.join(os.path.dirname(__file__), 'doc')
long_description = """\
The main website for ryppl is `ryppl.org
<http://ryppl.org>`_.  You can install
the `in-development version <http://github.com/ryppl/ryppl/archives/master>`_
of pip with ``easy_install ryppl==dev`` (or ``pip install ryppl==dev`` if you have pip).
"""

distutils2_pkg = os.path.join('submodule','distutils2','src')

setup(name='ryppl',
      version=version,
      description="A Git-based Software Development / Testing / Installation System",
      long_description=long_description,
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators'
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Build Tools',
      ],
      keywords='easy_install distutils setuptools egg virtualenv',
      author='The Ryppl Project',
      author_email='ryppl-dev@groups.google.com',
      url='http://ryppl.org',
      license='MIT',

      install_requires=['pip>=0.8'],
      # dependency_links=[
      #   'http://github.com/ryppl/pip/zipball/master#egg=pip',
      #   'http://bitbucket.org/tarek/distutils2/get/7eff59171017.gz#egg=distutils2'
      #  ],
      #install_requires=['distutils2'],
      
      # It is somewhat evil to install pip and distutils2 this way; we should be
      # declaring them as a dependencies and allowing setuptools.setup()
      # to fetch it as necessary, but I'm not yet sure how to declare
      # such dependencies.  In the meantime, this works.
      packages=find_packages('src')
      + find_packages(distutils2_pkg)
      ,

      package_dir = dict(
        ryppl=os.path.join('src','ryppl'), 
        distutils2=os.path.join(distutils2_pkg,'distutils2')
        ),

      entry_points=dict(console_scripts=['ryppl=ryppl:main']),
      )
