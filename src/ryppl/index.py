import pip.index
import pkg_resources
from ryppl.vcs.git import Git
import re

class PackageFinder(pip.index.PackageFinder):

    def __init__(self, develop=False, *args, **kw):
        self.develop = develop
        super(PackageFinder,self).__init__(*args, **kw)
    
    def _link_package_versions(self, link, search_name):
        
        explicit_versions = super(PackageFinder,self)._link_package_versions(link, search_name)
        git_versions = self._git_versions(link)

        for source in (git_versions,explicit_versions)[::1 if self.develop else -1]:
            for x in source: yield x

    def _git_versions(self, link):
        if not link.scheme in Git.schemes:
            return

        for version, ref, rev in Git(link.url).get_remote_refs():
            yield (pkg_resources.parse_version(version),
                   pip.index.Link(
                    re.sub('($|[#?].*)', '@'+ref+r'\1', link.url), # inserting version
                    link.comes_from),
                   version)
