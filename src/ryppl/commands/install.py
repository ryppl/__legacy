import pip.commands.install
from ryppl.index import PackageFinder

class InstallCommand(pip.commands.install.InstallCommand):
                

    def _build_package_finder(self, options, index_urls):
        """
        Create a package finder appropriate to this install command.
        This method is meant to be overridden by subclasses, not
        called directly.
        """
        return PackageFinder(find_links=options.find_links, index_urls=index_urls)

InstallCommand()
