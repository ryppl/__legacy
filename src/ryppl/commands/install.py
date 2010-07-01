import pip.commands.install

class InstallCommand(pip.commands.install.InstallCommand):
    """
    Ryppl's install command
    """

    def _build_package_finder(self, options, index_urls):
        """
        Ryppl's install command is exactly like PIP's, except that we
        use our own PackageFinder that can extract version numbers
        from tags in a Git repository.
        """
        from ryppl.index import PackageFinder
        return PackageFinder(find_links=options.find_links, index_urls=index_urls)

# Creating an instance of a pip command registers it.  Since pip's
# install command already registered itself, this will replace it with
# ours.
InstallCommand()
