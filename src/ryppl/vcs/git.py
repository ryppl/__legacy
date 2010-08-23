from pip import call_subprocess
from pip.vcs import vcs
from pip.vcs.git import Git as PipGit
from pip.log import logger
import os

class Git(PipGit):
    def unpack(self, location):
        """Clone the Git repository at a specific revision"""
        url, rev = self.get_url_rev()

        logger.notify('Cloning Git repository %s @%s to %s' % (url, rev, location))
        logger.indent += 2
        try:
            if os.path.exists(location):
                os.rmdir(location)
            call_subprocess(
                [self.cmd, 'clone', '-b', rev or 'HEAD', url, location],
                filter_stdout=self._filter, show_stdout=False)
        finally:
            logger.indent -= 2

    def get_remote_refs(self, *ls_remote_args):
        """
        Return an iterator over triples (pipversion, ref, SHA1) for
        each symbolic reference in the repository, where pipversion is
        a version number in pip format, ref is the symbolic name for
        that revision in the repository, and SHA1 is that revision's
        immutable revision number.
        """
        url,rev = self.get_url_rev()
        remote_refs = call_subprocess(
            (self.cmd, 'ls-remote')+ ls_remote_args + (url,), show_stdout=False)

        return ((ref.rsplit('/',1)[-1], ref, sha) for (sha,ref) in 
                (line.strip().split() for line in remote_refs.splitlines() ))
    
    
vcs.unregister(PipGit)
vcs.register(Git)
