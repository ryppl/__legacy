import sys
import pkgtest
from urllib import pathname2url
from cStringIO import StringIO
from pkgtest import mktree
from path import Path

here = Path(__file__).abspath.folder

class Environment(pkgtest.Environment):
    
    def __init__(self, environ=None):
        super(Environment,self).__init__(environ=environ)

        # Uninstall whatever version of pip came with the virtualenv.
        # Earlier versions of pip were incapable of
        # self-uninstallation on Windows, so first we upgrade, then we uninstall
        self.run('easy_install', '--upgrade', 'pip')
        
        # But invoking 'pip uninstall pip' will attempt to delete the
        # very executable that is running, so instead we do it via Python
        self.run('python', '-c', 'import pip;pip.main(["uninstall","-y","pip"])')

        # Install this version instead
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

        
def create_projects(env, **projects):
    from distutils2.metadata import DistributionMetadata

    index = env.scratch_path/'index'
    mktree(index)
    repo = env.scratch_path/'repo'
    
    open(index/'index.html', 'w').write(
        '\n'.join(
            ['<html><head><title>Simple Index</title></head><body>']
            + [ '<a href=%r/>%s</a><br/>' % (p,p) for p in projects ]
            + ['</body></html>'])
        )
    
    paths = {}

    for p,metadata in projects.items():

        mktree(index/p)
        
        root = repo/p
        paths[p] = root
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
        
    return index,paths

def reset():
    return ryppl_test.Environment()

