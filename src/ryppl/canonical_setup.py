import os, sys

from distutils2.metadata import DistributionMetadata
import os

# This option not working (yet)
use_distutils2 = '--distutils2' in sys.argv

if use_distutils2:
    from distutils2 import setup, find_packages
else:
    from setuptools import setup, find_packages

metadata = DistributionMetadata(
    path=os.path.join(os.getcwd(), '.ryppl', 'METADATA'),
    platform_dependant=True
    )

doc_dir = os.path.join(os.path.dirname(__file__), 'docs')

simple_kw_map = dict(summary='description', )
def metadata_to_setup_keywords(metadata):
        
    if use_distutils2:
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
        # copied these keywords out of the distutils source
        return dict(
          # 'distclass': ???
          # 'script_name':???
          # 'script_args', ???
          # 'options', ???
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


setup( **metadata_to_setup_keywords(metadata) )
