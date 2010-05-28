import os, sys, tempfile, shutil, glob, atexit, textwrap
from scripttest import TestFileEnvironment
from path import Path

exe_ext = '.EXE' if sys.platform == 'win32' else ''

#
# Filesystem utilities
#
def mktree(path):
    """
    Make the directory at path if it doesn't already exist
    """
    if not os.path.isdir(path): 
        os.makedirs(path)
    
def rmtree(path, ignore_errors=False):
    """
    Remove the directory tree at path.
    Exactly like shutil.rmtree, but will try to fix up permissions before deleting if necessary
    """
    # From pathutils by Michael Foord: http://www.voidspace.org.uk/python/pathutils.html
    def onerror(func, path, exc_info):
        """
        Error handler for ``shutil.rmtree``.

        If the error is due to an access error (read only file)
        it attempts to add write permission and then retries.

        If the error is for another reason it re-raises the error.

        Usage : ``shutil.rmtree(path, onerror=onerror)``

        """
        import stat
        if not os.access(path, os.W_OK):
            # Is the error an access error ?
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            raise

    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=ignore_errors, onerror=onerror)


#
# A mkdtemp with a cleanup routine that fires automatically atexit
#
_temp_dirs = []
def mkdtemp(*args, **kw):
    """
    Make a temporary directory that will be automatically cleaned up
    unless PKGTEST_NO_CLEANUP is set in the environment (useful for
    testing if you want to inspect the results afterward).  Exactly
    like tempfile.mkdtemp except that this one cleans up
    automatically.
    """
    dir = tempfile.mkdtemp(*args,**kw)
    global _temp_dirs
    # Check whether cleanup has been suppressed for testing purposes
    if not os.environ.has_key('PKGTEST_NO_CLEANUP'):
        _temp_dirs.append(dir)
    return Path(dir)

def _cleanup_dirs(dirs):
    for d in dirs:
        rmtree(d, ignore_errors=True)

atexit.register(lambda dirs=_temp_dirs: _cleanup_dirs(dirs))

#
def relpath(root, other):
    """
    a poor man's os.path.relpath, since we may not have Python 2.6
    """
    prefix = root+os.path.sep
    assert other.startswith(prefix)
    return Path(other[len(prefix):])


#
# Testing Environment utilities
#
def create_virtualenv(where=None, distribute=False, **kw):
    """
    Create a virtual Python environment for testing purposes.  If
    distribute is True, installs the distribute package in place of
    setuptools.

    Returns the directory of the environment itself, its Python
    library directory (which contains site-packages), its 'include'
    and binary file directory (bin, or on windows, Scripts)
    respectively.  Additional keyword arguments are passed to mkdtemp
    to create the virtual environment directory.
    """
    save_argv = sys.argv

    if not where:
        where = mkdtemp(**kw)

    try:
        import virtualenv
        distribute_opt = ['--distribute'] if distribute else []
        sys.argv = ['virtualenv', '--quiet'] + distribute_opt + ['--no-site-packages', '--unzip-setuptools', where]
        virtualenv.main()
    finally: 
        sys.argv = save_argv

    return virtualenv.path_locations(where)

def install_setuptools(env):
    """
    Make sure a very recent setuptools is installed
    """
    easy_install = os.path.join(env.bin_path, 'easy_install')
    version = 'setuptools==0.6c11'
    if sys.platform != 'win32':
        return env.run(easy_install, version)
    
    tempdir = tempfile.mkdtemp()
    try:
        for f in glob.glob(easy_install+'*'):
            shutil.copy2(f, tempdir)
        return env.run(os.path.join(tempdir, 'easy_install'), version)
    finally:
        shutil.rmtree(tempdir)

class TestResult(object):
    """
    A wrapper over ScriptTest's ProcResult that adds some niceties.
    """

    def __init__(self, impl, verbose=False):
        """
        Wraps the ProcResult impl.  
        If verbose is True, dump impl's stdout and stderr.
        """
        self._impl = impl
        
        if verbose:
            print '======= stdout ========'
            print self.stdout

            if self.stderr:
                print '======= stderr ========'
                print self.stderr
            print '======================='

    def __getattr__(self, attr):
        """Forwards most everything to its ProcResult implementation"""
        return getattr(self._impl,attr)

    # Newline adjustment for win32
    if sys.platform == 'win32':
        @property
        def stdout(self):
            return self._impl.stdout.replace('\r\n', '\n')

        @property
        def stderr(self):
            return self._impl.stderr.replace('\r\n', '\n')
            
        def __str__(self):
            return str(self._impl).replace('\r\n','\n')
    else:
        # Python doesn't automatically forward __str__ through __getattr__
        def __str__(self):
            return str(self._impl)

download_cache = mkdtemp(prefix='pip-cache')

class Environment(TestFileEnvironment):
    """
    A specialized TestFileEnvironment for tests of
    packaging/installation functionality
    """

    #
    # Attribute naming convention
    # ---------------------------
    # 
    # Instances of this class have several attributes representing paths
    # in the filesystem.  To keep things straight, absolute paths have
    # a name of the form xxxx_path and relative paths have a name that
    # does not end in '_path'.

    # The following paths are relative to the root_path, and should be
    # treated by clients as instance attributes.  The fact that they
    # are defined in the class is an implementation detail

    # where we'll create the virtual Python installation for testing
    #
    # Named with a leading dot to reduce the chance of spurious
    # results due to being mistaken for the virtualenv package.
    venv = Path('.virtualenv') 

    # The root of a directory tree to be used arbitrarily by tests
    scratch = Path('scratch')

    verbose = False

    def __init__(self, environ=None):
        
        self.root_path = mkdtemp(prefix='pkgtest')

        # We will set up a virtual environment at root_path.  
        self.scratch_path = self.root_path / self.scratch

        self.venv_path = self.root_path / self.venv

        if not environ:
            environ = dict(((k, v) for k, v in os.environ.items()
                if not k.lower().startswith('pip_')))
            environ['PIP_DOWNLOAD_CACHE'] = str(download_cache)

        environ['PIP_NO_INPUT'] = '1'
        environ['PIP_LOG_FILE'] = str(self.root_path/'pip-log.txt')

        super(Environment,self).__init__(
            self.root_path, ignore_hidden=False, 
            environ=environ, split_cmd=False, start_clear=False,
            cwd=self.scratch_path, capture_temp=True, assert_no_temp=True
            )

        mktree(self.venv_path)
        mktree(self.scratch_path)

        use_distribute = os.environ.get('PKGTEST_USE_DISTRIBUTE', False)

        # Create a virtualenv and remember where it is putting things.
        virtualenv_paths = create_virtualenv(self.venv_path, distribute=use_distribute)

        assert self.venv_path == virtualenv_paths[0] # sanity check

        for id,path in zip(('venv', 'lib', 'include', 'bin'), virtualenv_paths):
            setattr(self, id+'_path', Path(path))
            setattr(self, id, relpath(self.root_path,path))
            
        assert self.venv == Environment.venv # sanity check

        self.site_packages = self.lib/'site-packages'
        self.site_packages_path = self.lib_path/'site-packages'

        # put the virtualenv's bin dir first on the PATH; that's
        # essentially all that happens when you activate a virtualenv
        self.environ['PATH'] = Path.pathsep.join( (self.bin_path, self.environ['PATH']) )

        # test that test-scratch virtualenv creation produced sensible venv python
        pythonbin = self.run('python', '-c', 'import sys; print sys.executable').stdout.strip()
        if Path(pythonbin).noext != self.bin_path/'python':
            raise RuntimeError(
                "Oops! 'python' in our test environment runs %r" 
                " rather than expected %r" % (pythonbin, self.bin_path/'python'))

        # make sure we have current setuptools to avoid svn incompatibilities
        if not use_distribute:
            install_setuptools(self)

    def run(self, *args, **kw):
        if self.verbose:
            print '>> running', args, kw
        cwd = kw.pop('cwd', None)

        return TestResult( super(Environment,self).run(cwd=cwd,*args,**kw), verbose=self.verbose )

    def __del__(self):
        shutil.rmtree(self.root_path, ignore_errors=True)

def run_pip(*args, **kw):
    return env.run('pip', *args, **kw)

def write_file(filename, text, dest=None):
    """Write a file in the dest (default=env.scratch_path)
    
    """
    env = get_env()
    if dest:
        complete_path = dest/ filename
    else:
        complete_path = env.scratch_path/ filename
    f = open(complete_path, 'w')
    f.write(text)
    f.close()

def mkdir(dirname):
    os.mkdir(os.path.join(get_env().scratch_path, dirname))

def get_env():
    if env is None:
        reset_env()
    return env

try:
    any
except NameError:
    def any(seq):
        for item in seq:
            if item:
                return True
        return False

# FIXME ScriptTest does something similar, but only within a single
# ProcResult; this generalizes it so states can be compared across
# multiple commands.  Maybe should be rolled into ScriptTest?
def diff_states(start, end, ignore=None):
    """
    Differences two "filesystem states" as represented by dictionaries
    of FoundFile and FoundDir objects.

    Returns a dictionary with following keys:

    ``deleted``
        Dictionary of files/directories found only in the start state.

    ``created``
        Dictionary of files/directories found only in the end state.

    ``updated``
        Dictionary of files whose size has changed (FIXME not entirely
        reliable, but comparing contents is not possible because
        FoundFile.bytes is lazy, and comparing mtime doesn't help if
        we want to know if a file has been returned to its earlier
        state).

    Ignores mtime and other file attributes; only presence/absence and
    size are considered.

    """
    ignore = ignore or []
    # FIXME: this code ignores too much, e.g. foo/bar when only foo/b is specified
    start_keys = set([k for k in start.keys()
                      if not any([k.startswith(i) for i in ignore])])
    end_keys = set([k for k in end.keys()
                    if not any([k.startswith(i) for i in ignore])])
    deleted = dict([(k, start[k]) for k in start_keys.difference(end_keys)])
    created = dict([(k, end[k]) for k in end_keys.difference(start_keys)])
    updated = {}
    for k in start_keys.intersection(end_keys):
        if (start[k].size != end[k].size):
            updated[k] = end[k]
    return dict(deleted=deleted, created=created, updated=updated)

def assert_all_changes( start_state, end_state, expected_changes ):
    """
    Fails if anything changed that isn't listed in the
    expected_changes.  

    start_state is either a dict mapping paths to
    scripttest.[FoundFile|FoundDir] objects or a TestResult whose
    files_before we'll test.  end_state is either a similar dict or a
    TestResult whose files_after we'll test.

    Note: listing a directory means anything below
    that directory can be expected to have changed.
    """
    start_files = start_state
    end_files = end_state
    if isinstance(start_state, TestResult):
        start_files = start_state.files_before
    if isinstance(end_state, TestResult):
        end_files = end_state.files_after

    diff = diff_states( start_files, end_files, ignore=expected_changes )
    if diff.values() != [{},{},{}]:
        import pprint
        raise TestFailure, 'Unexpected changes:\n' + '\n'.join(
            [k + ': ' + ', '.join(v.keys()) for k,v in diff.items()])

    # Don't throw away this potentially useful information
    return diff
