import pip.index
import pkg_resources
from ryppl.vcs.git import Git
import re

class PackageFinder(pip.index.PackageFinder):
    """
    Ryppl's PackageFinder yields the version tags from a Git repo
    """

    def __init__(self, develop=False, *args, **kw):
        # If the user issued the 'develop' command, remember that
        self.develop = develop
        super(PackageFinder,self).__init__(*args, **kw)
    
    def _link_package_versions(self, link, search_name):
        """
        A generator that yields a triple for each version accessible
        through the given link.  Ours can find versions in git ref
        names
        """
        
        # Let the base class get any versions it can find.  Typically,
        # that is one or zero versions, depending on whether the link
        # is recognized as a tarball
        explicit_versions = super(PackageFinder,self)._link_package_versions(link, search_name)

        # Collect all the versions accessible when the link is
        # interpreted as the URI of a git repository
        git_versions = self._git_versions(link)

        # catenate all the versions together, but if the user issued
        # the 'develop' command, prefer those that come from a Git
        # repo so he will get a clone to work with.
        for source in (git_versions,explicit_versions)[::1 if self.develop else -1]:
            for x in source: yield x

            
    def _git_versions(self, link):
        # Bail if the link doesn't have a URI scheme that Git
        # recognizes
        if not link.scheme in Git.schemes:
            return

        # Iterate all the remote references and produce a triple
        # consisting of a PIP version string, a Link for the URL with
        # appended @+ref name, and the page where the original link
        # was found.
        for version, ref, rev in Git(link.url).get_remote_refs():
            yield (pkg_resources.parse_version(version),
                   pip.index.Link(
                    re.sub('($|[#?].*)', '@'+ref+r'\1', link.url), # inserting version
                    link.comes_from),
                   version)
