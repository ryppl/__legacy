import pip.commands.install

class InstallCommand(pip.commands.install.InstallCommand):
    """
    Ryppl's install command
    """

    def __init__(self):
        """
        We tweak Ryppl's install command so that it has a different
        default index URL.
        """
        super(InstallCommand, self).__init__()
        # change the default location of the index.
        self.parser.remove_option('-i')
        self.parser.add_option(
            '-i', '--index-url',
            dest='index_url',
            metavar='URL',
            default='http://ryppl.github.com/index',
            help='Base URL of Ryppl Package Index (default %default)')

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
