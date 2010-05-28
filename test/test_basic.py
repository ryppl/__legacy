import os,sys
from path import Path
from pkgtest import mktree
from urllib import pathname2url
from cStringIO import StringIO
from ryppl_test import Environment as new_test, create_projects

here = Path(__file__).abspath.folder
distutils2_src = here.folder/'submodule'/'distutils2'/'src'

try:
    import distutils2
except ImportError:
    sys.path.insert(0, distutils2_src)
    import distutils2

from distutils2.metadata import DistributionMetadata as METADATA

def test_fetch():
    env = new_test()
    index,project_paths = create_projects(
        env, my_proj=open(distutils2_src/'distutils2'/'tests'/'PKG-INFO').read())
    env.ryppl('install', '--no-install', '-vvv', '-i', 'file://'+pathname2url(index), 'my_proj')

def test_diamond():
    env = new_test()
    index,project_paths = create_projects(
        env,
        ProjA=dict(requires_dist=['ProjB','ProjC']),
        ProjB=dict(requires_dist=['ProjD<1.0']),
        ProjC=dict(requires_dist=['ProjD>1.0']),
        ProjD=dict(),
        )

    d = project_paths['ProjD']
    env.run('git', 'tag', '0.9', cwd=d)
    open(d/'later','w').write('update project')
    env.run('git', 'add', 'later', cwd=d)
    env.run('git', 'commit', '-m', 'update', cwd=d)
    env.run('git', 'tag', '1.1', cwd=d)
    env.ryppl('install', 
          # '--no-install', 
          '-vvv', 
          '-i', 'file://'+pathname2url(index), 'ProjA')

if __name__ == '__main__':
    test_diamond()
