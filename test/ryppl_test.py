import os
import sys
import pkgtest
from urllib import pathname2url
from cStringIO import StringIO
from pkgtest import mktree
from path import Path
import glob
import testutil
import shutil
from urllib import pathname2url

here = Path(__file__).abspath.folder

class Environment(pkgtest.Environment):
    """
    Specialized package testing pkgtest.Environment for testing ryppl.
    """
    def __init__(self, environ=None):
        super(Environment,self).__init__(environ=environ)

        tmppath = Path(testutil.mkdtemp())

        # On Windows, we can't use pip to upgrade the pip package because
        # it fails upgrading the pip.exe that is currently running.
        # So, we copy all of pip from the bin_path to some temporary
        # directory and invoke it from there.
        for pip in glob.glob(self.bin_path/'pip*'):
           shutil.copy2(pip, tmppath) 

        pip_exe = tmppath/'pip'+testutil.exe_ext
        self.run(pip_exe, 'install', '--upgrade', 'pip')

        # Now, we install ryppl by running it's setup.py from
        # the ryppl/ directory (one directory up)
        self.run('python', 'setup.py', 'install', cwd=here.folder)

    def ryppl(self, *args, **kw):
        if '--pdb' in sys.argv:
            # Get the repr() of ryppl's __init__.py, so we can strip
            # it and preserve any spaces
            module_file = self.run('python','-c', 'import ryppl,os,sys;sys.stdout.write(os.path.abspath(ryppl.__file__))').stdout
            if module_file.endswith('.pyo') or module_file.endswith('.pyc'):
                module_file = module_file[:-1]
            
            return self.run(
                'python', '-u', '-m', 'pdb', module_file, debug=True, *args, **kw)
        else:
            return self.run('ryppl', *args, **kw)


class Project(object):

    def __init__(self, name, path, env):
        self.name = name
        self.path = path
        self.env = env

    def add_file(self, file_path, contents):
        fullpath = os.path.abspath(os.path.join(self.path, file_path))
        dir = os.path.dirname(fullpath)
        mktree(dir)
        open(fullpath, 'w').write(contents)
        self.env.run('git', 'add', file_path, cwd=self.path)
        self.env.run('git', 'commit', '--amend', '-m', 'initial checkin', cwd=self.path)

def create_projects(env, **proj_metadata):
    """
    Create git repositories and an index for projects within env.

    env should be an Environment

    proj_metadata should be a dict mapping project names to
    DistributionMetadata objects representing their metadata.  

    Returns (index,projdirs) where:

    * index is the path to the locally-generated index

    * projdirs is a dict mapping project names to the paths to the
      locally-generated git repositories.
    """
    from distutils2.metadata import DistributionMetadata

    index = env.scratch_path/'index'
    mktree(index)
    repo = env.scratch_path/'repo'
    
    open(index/'index.html', 'w').write(
        '\n'.join(
            ['<html><head><title>Simple Index</title></head><body>']
            + [ '<a href=%r/>%s</a><br/>' % (p,p) for p in proj_metadata ]
            + ['</body></html>'])
        )
    
    projects = {}

    for p,metadata in proj_metadata.items():

        mktree(index/p)
        
        root = repo/p
        projects[p] = Project(p, root, env)
        mktree(root)

        env.run('git', 'init', cwd = root)

        dot_ryppl = root/'.ryppl'

        if isinstance(metadata, basestring):
            m = DistributionMetadata()
            m.read_file(StringIO(metadata))
            metadata = m
        elif isinstance(metadata, dict):
            m = DistributionMetadata()
            for k,v in metadata.items():
                m[k] = v
            metadata = m

        metadata['Name'] = p
        if metadata['Version'] == 'UNKNOWN':
            metadata['Version'] = '0.9'
        if metadata['Requires-Python'] == 'UNKNOWN':
            metadata['Requires-Python'] = '>2.0'
            

        mktree(dot_ryppl)
        metadata.write(dot_ryppl/'METADATA')

        # mktree(root/p)
        # open(root/p/'__init__.py', 'w').write('print "importing module %s"' % p)

        env.run('git', 'add', '*', Path('.ryppl')/'*', cwd = root)
        env.run('git', 'commit', '-m', 'initial checkin', cwd = root)

        repo_url = pathname2url(root)

        open(index/p/'index.html', 'w').write(
            '<html><head><title>Links for %(p)s</title></head>'
            '<body>'
            '<h1>Links for %(p)s</h1>'
            '<a href="git+file://%(repo_url)s#egg=%(p)s">Git Repository</a><br/>'
            '</body></html>'
            % locals()
            )
        
    return 'file://'+pathname2url(index),projects

def reset():
    return ryppl_test.Environment()

