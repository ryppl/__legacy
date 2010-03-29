"""distutils.command.check

Implements the Distutils 'check' command.
"""
__revision__ = "$Id: check.py 75266 2009-10-05 22:32:48Z andrew.kuchling $"

from distutils2.core import Command
from distutils2.errors import DistutilsSetupError

class check(Command):
    """This command checks the meta-data of the package.
    """
    description = ("perform some checks on the package")
    user_options = [('metadata', 'm', 'Verify meta-data'),
                    ('restructuredtext', 'r',
                     ('Checks if long string meta-data syntax '
                      'are reStructuredText-compliant')),
                    ('strict', 's',
                     'Will exit with an error if a check fails')]

    boolean_options = ['metadata', 'restructuredtext', 'strict']

    def initialize_options(self):
        """Sets default values for options."""
        self.restructuredtext = 0
        self.metadata = 1
        self.strict = 0
        self._warnings = 0

    def finalize_options(self):
        pass

    def warn(self, msg):
        """Counts the number of warnings that occurs."""
        self._warnings += 1
        return Command.warn(self, msg)

    def run(self):
        """Runs the command."""
        # perform the various tests
        if self.metadata:
            self.check_metadata()
        if self.restructuredtext:
            if self.distribution.metadata.docutils_support:
                self.check_restructuredtext()
            elif self.strict:
                raise DistutilsSetupError('The docutils package is needed.')

        # let's raise an error in strict mode, if we have at least
        # one warning
        if self.strict and self._warnings > 0:
            raise DistutilsSetupError('Please correct your package.')

    def check_metadata(self):
        """Ensures that all required elements of meta-data are supplied.

        name, version, URL, (author and author_email) or
        (maintainer and maintainer_email)).

        Warns if any are missing.
        """
        missing, __ = self.distribution.metadata.check()
        if missing != []:
            self.warn("missing required meta-data: %s"  % ', '.join(missing))

    def check_restructuredtext(self):
        """Checks if the long string fields are reST-compliant."""
        missing, warnings = self.distribution.metadata.check()
        for warning in warnings:
            line = warning[-1].get('line')
            if line is None:
                warning = warning[1]
            else:
                warning = '%s (line %s)' % (warning[1], line)
            self.warn(warning)

