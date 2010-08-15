import os, sys
from distutils2.metadata import DistributionMetadata

# This option not working (yet).  Should we use setup() from distutils2?
use_distutils2 = '--distutils2' in sys.argv

if use_distutils2:
    from distutils2 import setup
else:
    from setuptools import setup
    from setuptools.command.install import install
    from distutils.command.build import build

    # setuptools command object to execute during ryppl build
    class cmake_build(build):
      def run (self):
        print "cmake_build!!!"
        pass

    # setuptools command object to execute during ryppl install
    class cmake_install(install):
      def run (self):
        print "cmake_install!!!"
        # Must build before we can install
        self.run_command('build')
        pass

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
          # Meaning: The Distribution class to use.
          # Type: A subclass of distutils.core.Distribution
          # 'distclass': ???
          
          # Meaning: The name of the setup.py script - defaults to sys.argv[0].
          # Type: a string
          # 'script_name':???
          
          # Meaning: Arguments to supply to the setup script.
          # Type: a list of strings
          # 'script_args', ???
          
          # Meaning: default options for the setup script.
          # Type: a string
          # 'options', ???

          # Copied from setuputils/dist.py. Looks like these could be useful.
          #'extras_require' -- a dictionary mapping names of optional "extras" to the
          #     additional requirement(s) that using those extras incurs. For example,
          #     this::
          #
          #     extras_require = dict(reST = ["docutils>=0.3", "reSTedit"])
          #
          #     indicates that the distribution can optionally provide an extra
          #     capability called "reST", but it can only be used if docutils and
          #     reSTedit are installed.  If the user installs your package using
          #     EasyInstall and requests one of your extras, the corresponding
          #     additional requirements will be installed if needed.
          # 
          #'features' -- a dictionary mapping option names to 'setuptools.Feature'
          #   objects.  Features are a portion of the distribution that can be
          #   included or excluded based on user options, inter-feature dependencies,
          #   and availability on the current system.  Excluded features are omitted
          #   from all setup commands, including source and binary distributions, so
          #   you can create multiple distributions from the same source tree.
          #   Feature names should be valid Python identifiers, except that they may
          #   contain the '-' (minus) sign.  Features can be included or excluded
          #   via the command line options '--with-X' and '--without-X', where 'X' is
          #   the name of the feature.  Whether a feature is included by default, and
          #   whether you are allowed to control this from the command line, is
          #   determined by the Feature object.  See the 'Feature' class for more
          #   information.
          #
          #'test_suite' -- the name of a test suite to run for the 'test' command.
          #   If the user runs 'python setup.py test', the package will be installed,
          #   and the named test suite will be run.  The format is the same as
          #   would be used on a 'unittest.py' command line.  That is, it is the
          #   dotted name of an object to import and call to generate a test suite.
          #
          #'package_data' -- a dictionary mapping package names to lists of filenames
          #   or globs to use to find data files contained in the named packages.
          #   If the dictionary has filenames or globs listed under '""' (the empty
          #   string), those names will be searched for in every package, in addition
          #   to any names for the specific package.  Data files found using these
          #   names/globs will be installed along with the package, in the same
          #   location as the package.  Note that globs are allowed to reference
          #   the contents of non-package subdirectories, as long as you use '/' as
          #   a path separator.  (Globs are automatically converted to
          #   platform-specific paths at runtime.)

          # This hooks the "build" and "install" commands to do our bidding.
          cmdclass = {'build': cmake_build, 'install': cmake_install},

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
