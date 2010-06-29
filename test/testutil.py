import os, sys, shutil, atexit, tempfile
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


