"""distutils.archive_util

**This module will be removed from Python in the next version (3.3)**

Utility functions for creating archive files (tarballs, zip files,
that sort of thing)."""

__revision__ = "$Id: archive_util.py 75659 2009-10-24 13:29:44Z tarek.ziade $"

from warnings import warn
import shutil
from distutils2.log import _global_log as logger

_DEPRECATION_MSG = '%(name)s is deprecated in favor of shutil.%(name)s'

def make_archive(base_name, format, root_dir=None, base_dir=None, verbose=0,
                 dry_run=0, owner=None, group=None):
    warn(_DEPRECATION_MSG % {'name': 'make_archive'},
         PendingDeprecationWarning)
    return shutil.make_archive(base_name, format, root_dir, base_dir,
                               verbose, dry_run, owner, group, logger)

def make_tarball(base_name, base_dir, compress="gzip", verbose=0, dry_run=0,
                 owner=None, group=None):
    warn(_DEPRECATION_MSG % {'name': 'make_tarball'},
         PendingDeprecationWarning)
    return shutil._make_tarball(base_name, base_dir, compress, verbose,
                                dry_run, owner, group, logger)

def make_zipfile(base_name, base_dir, verbose=0, dry_run=0):
    warn(_DEPRECATION_MSG % {'name': 'make_tarball'},
         PendingDeprecationWarning)
    try:
        return shutil._make_zipfile(base_name, base_dir, verbose, dry_run,
                                    logger)
    except shutil.ExecError, e:
        # make sure we return the old exception
        # so existing code is not impacted
        from distutils2.errors import DistutilsExecError
        raise DistutilsExecError(e.msg)

ARCHIVE_FORMATS = shutil._ARCHIVE_FORMATS

def check_archive_formats(formats):
    """Returns the first format from the 'format' list that is unknown.

    If all formats are known, returns None
    """
    warn("check_archive_formats will be removed in 3.4",
         PendingDeprecationWarning)
    for format in formats:
        if format not in ARCHIVE_FORMATS:
            return format
    return None

