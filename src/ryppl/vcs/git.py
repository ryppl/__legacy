from pip import call_subprocess
from pip.vcs.git import Git as PipGit
from pip.log import logger

class Git(PipGit):
    def unpack(self, location):
        """Clone the Git repository at the url to the destination location"""
        url, rev = self.get_url_rev()

        logger.notify('Cloning Git repository %s to %s' % (url, location))
        logger.indent += 2
        try:

            if os.path.exists(location):
                os.rmdir(location)
            if not rev:
                rev = 'HEAD'
            call_subprocess(
                [self.cmd, 'clone', '-n', url, location],
                filter_stdout=self._filter, show_stdout=False)
            call_subprocess(
                [self.cmd, 'checkout', '-b', rev],
                filter_stdout=self._filter, show_stdout=False, cwd=location)
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
    
    
