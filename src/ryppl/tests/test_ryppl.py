import os,sys

# the ryppl/tests/ subdirectory
here = os.path.dirname(os.path.abspath(__file__))

# Make the pip test facilities available
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(here)), 'tests'))

from path import Path
from test_pip import reset_env, demand_dirs
from urllib import pathname2url
from cStringIO import StringIO

here = Path(here)

try:
    import distutils2
except ImportError:
    sys.path.insert(0, here.folder.folder/'distutils2'/'src')
    import distutils2

from distutils2.metadata import DistributionMetadata as METADATA

def create_projects(env, **projects):
    index = env.scratch_path/'index'
    demand_dirs(index)
    repo = env.scratch_path/'repo'
    
    open(index/'index.html', 'w').write(
        '\n'.join(
            ['<html><head><title>Simple Index</title></head><body>']
            + [ '<a href=%r/>%s</a><br/>' % (p,p) for p in projects ]
            + ['</body></html>'])
        )
    
    paths = {}

    for p,metadata in projects.items():

        demand_dirs(index/p)
        
        root = repo/p
        paths[p] = root
        demand_dirs(root)

        env.run('git', 'init', cwd = root)

        dot_ryppl = root/'.ryppl'

        if isinstance(metadata, basestring):
            m = METADATA()
            m.read_file(StringIO(metadata))
            metadata = m
        elif isinstance(metadata, dict):
            m = METADATA()
            for k,v in metadata.items():
                m[k] = v
            metadata = m

        metadata['Name'] = p
        if metadata['Version'] == 'UNKNOWN':
            metadata['Version'] = '0.9'
        if metadata['Requires-Python'] == 'UNKNOWN':
            metadata['Requires-Python'] = '>2.0'
            

        demand_dirs(dot_ryppl)
        metadata.write(dot_ryppl/'METADATA')

        # demand_dirs(root/p)
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
    return reset_env()

def ryppl(env, *args, **kw):
    if '--pdb' in sys.argv:
        return env.run(
            'python', '-u', '-m', 'pdb', here.folder.folder/'rypscript.py', debug=True, *args, **kw)
    else:
        return env.run('ryppl', *args, **kw)

def test_fetch():
    env = reset()
    index,project_paths = create_projects(
        env, my_proj=open(here.folder.folder/'distutils2'/'src'/'distutils2'/'tests'/'PKG-INFO').read())
    ryppl(env, 'install', '--no-install', '-v', '-i', 'file://'+pathname2url(index), 'my_proj')

def test_diamond():
    env = reset()
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
    ryppl(env, 'install', 
          # '--no-install', 
          '-v', 
          '-i', 'file://'+pathname2url(index), 'ProjA')

if __name__ == '__main__':
    test_diamond()
