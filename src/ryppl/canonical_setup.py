import os, sys, shutil
from subprocess import check_call
from distutils2.metadata import DistributionMetadata

# This are global constants. Do not change.
is_win32 = (sys.platform == 'win32')

# This option not working (yet).  Should we use setup() from distutils2?
use_distutils2 = '--distutils2' in sys.argv

if use_distutils2:
    from distutils2 import setup
else:
    from setuptools import setup
    from setuptools.command.egg_info import egg_info as _egg_info
    from distutils.command.build import build as _build
    from setuptools.command.install import install as _install

    class cmake_egg_info(_egg_info):
      def run (self):
        # Record the egg info path someplace so that cmake_install
        # can find it later.
        with open('egg_info_path.txt', 'w') as egg_info:
          egg_info.writelines([os.path.join(os.getcwd(), self.egg_info)])
        _egg_info.run(self)

    # setuptools command object to execute during ryppl build
    class cmake_build(_build):
      def run (self):
        # If this is a cmake project, use cmake to build it.
        if os.path.isfile(os.path.join(os.getcwd(), 'CMakeLists.txt')):
          # Make the target directory if it doesn't exist already
          if not os.path.isdir(self.build_base):
            os.makedirs(self.build_base)
          # Configure cmake if it hasn't been done already.
          if not os.path.isfile(os.path.join(self.build_base, 'CMakeCache.txt')):
            check_call(['cmake', os.getcwd()], cwd=self.build_base, shell=is_win32)
          # actually build 
          check_call(['cmake', '--build', '.'], cwd=self.build_base, shell=is_win32)
        else:
          _build.run(self)

    # setuptools command object to execute during ryppl install
    class cmake_install(_install):
      def run (self):
        if os.path.isfile(os.path.join(os.getcwd(), 'CMakeLists.txt')):
          # Make sure the project is actually built first
          self.run_command('build')
          # Now install it.
          check_call(['cmake', '--build', '.', '--target', 'install'], cwd=self.build_base, shell=is_win32)
          # Copy the install_manifest.txt to the install record file
          print >>sys.stderr, 'record-install.txt =', self.record
          shutil.copy2(os.path.join(self.build_base, 'install_manifest.txt'), self.record)
          egg_info_path = '';
          with open('egg_info_path.txt', 'r') as egg_info:
            egg_info_path = egg_info.readline()
          with open(self.record, 'a+') as install_record:
            install_record.writelines([egg_info_path])
        else:
          _install.run(self)

# Read the metadata out of the project's .ryppl/METADATA file
metadata = DistributionMetadata(
    path=os.path.join(os.getcwd(), '.ryppl', 'METADATA'),
    platform_dependant=True
    )

def metadata_to_setup_keywords(metadata):
    """
    Convert a Distutils2 metadata object into a dict of named
    arguments to be passed to setup()
    """
    if use_distutils2:
        # Everything *should* be this easy.
        return dict( metadata.items() )
    else:
        class item_to_attribute(object):
            """
            because I hate seeing identifiers between quotes
            """
            def __init__(self, target):
                self.target = target

            def __getattr__(self, name):
                return self.target[name]

        m = item_to_attribute(metadata)
        # There's probably a more declarative way, but until then, I just
        # copied these keywords out of the distutils source.
        # EAN: these parameters are documented at
        # http://docs.python.org/distutils/apiref.html
        return dict(
          # This hooks various ryppl commands to do our bidding.
          cmdclass = {
            'egg_info'  : cmake_egg_info,
            'build'     : cmake_build,
            'install'   : cmake_install
          },

          name = m.name,
          version = m.version,
          author = m.author,
          author_email = m.author_email,
          maintainer = m.maintainer,
          maintainer_email = m.maintainer_email,
          url = m.project_url,
          description = m.summary,
          long_description = m.description,
          keywords = ' '.join(m.keywords),
          platforms = m.platform,
          classifiers = m.classifier, 
          download_url = m.download_url,
          install_requires = m.requires_dist or m.requires,
          provides = m.provides_dist or m.provides,
          obsoletes = m.obsoletes_dist or m.obsoletes,
          )

# Call setup with keyword arguments corresponding to the metadata
setup( **metadata_to_setup_keywords(metadata) )
