import sys, os
from subprocess import call, check_call, PIPE
from path import Path
import shutil
from tempfile import mkdtemp, gettempdir
from pkgtest import create_virtualenv, rmtree, mktree, exe_ext as EXE

use_distribute=False

def run(*args):
    if not use_distribute:
        check_call(args)
    else:
        env = os.environ.copy()
        env['PKG_TEST_USE_DISTRIBUTE']='1'
        check_call(args, env=env)

def assert_in_path(exe):
    returncode = call(
        [exe, '--version'], stdout=PIPE, shell=(sys.platform=='win32'))
    assert returncode == 0, '%s not found in PATH: %s' % (exe, os.environ['PATH'])

def clean(root):
    print >> sys.stderr, 'Cleaning ...',
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            if f.endswith('.pyc'):
                os.unlink(Path(dirpath)/f)
    rmtree(root/'build')
    rmtree(root/'dist')
    rmtree(root/'pip.egg-info')
    print >> sys.stderr, 'ok'


def main(argv):
    global use_distribute

    # Grab this script's options
    global use_distribute
    use_distribute = ('--distribute' in argv)
    prepare_env = [x for x in argv if x.startswith('--prepare-env=')]
    argv = [x for x in argv if x != '--distribute' and not x.startswith('--prepare-env=')]

    here = Path(sys.path[0])
    script_name = Path(__file__).name

    if not (here/script_name).exists:
        here = Path(__file__).abspath.folder
        assert (here/script_name).exists, "Can't locate directory of this script"

    # Make sure all external tools are set up to be used.
    print >> sys.stderr, 'Checking for installed prerequisites in PATH:',
    for tool in ('git',):
        print >> sys.stderr, tool,'...',
        assert_in_path(tool)
    print >> sys.stderr, 'ok'

    ryppl_root = here.folder

    #
    # Delete everything that could lead to stale test results
    #
    clean( ryppl_root )
    
    save_dir = os.getcwd()

    if prepare_env:
        venv_dir = prepare_env[-1][len('--prepare_env='):]
        mktree(venv_dir)
    else:
        venv_dir = mkdtemp('-ryppl_self_test')

    try:
        os.chdir(venv_dir)

        #
        # Prepare a clean, writable workspace
        #
        print >> sys.stderr, 'Preparing test environment ...'
        venv, lib, include, bin = create_virtualenv(venv_dir, distribute=use_distribute)

        abs_bin = Path(bin).abspath

        # Make sure it's first in PATH
        os.environ['PATH'] = str(
            Path.pathsep.join(( abs_bin, os.environ['PATH'] ))
            )

        #
        # Install python module testing prerequisites
        #
        pip_exe = abs_bin/'pip'+EXE
        download_cache = '--download-cache=' \
            + Path(gettempdir())/'ryppl-test-download-cache'
        def pip_install(*pkg):
            print >> sys.stderr, '   pip install',' '.join(pkg), '...',
            run(pip_exe, 'install', '-q', download_cache, *pkg)
            print >> sys.stderr, 'ok'
        pip_install('virtualenv')
        pip_install('--no-index', '-f', 'http://pypi.python.org/packages/source/n/nose/', 'nose')
        pip_install('scripttest>=1.0.4')
        print >> sys.stderr, 'ok'
        nosetests = abs_bin/'nosetests'+EXE
        test_cmd = [nosetests, '-w', ryppl_root/'test'] + argv
        if prepare_env:
            print 'Testing command:'
            print ' '.join(test_cmd)
        else:
            run( test_cmd )

    finally:
        os.chdir(save_dir)
        # Keep VCSes from seeing spurious new/changed files
        clean(ryppl_root)


if __name__ == '__main__':
    main( sys.argv[1:] )
