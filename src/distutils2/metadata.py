import os
import sys
import platform
from StringIO import StringIO
from email import message_from_file
from tokenize import tokenize, NAME, OP, STRING, ENDMARKER

from distutils2.util import rfc822_escape

# Encoding used for the PKG-INFO files
PKG_INFO_ENCODING = 'utf-8'


class DistributionMetadata(object):
    """Dummy class to hold the distribution meta-data: name, version,
    author, and so forth.
    """

    _METHOD_BASENAMES = ("name", "version", "author", "author_email",
                         "maintainer", "maintainer_email", "url",
                         "license", "description", "long_description",
                         "keywords", "platforms", "fullname", "contact",
                         "contact_email", "license", "classifiers",
                         "download_url",
                         # PEP 314
                         "provides", "requires", "obsoletes",
                         )

    def __init__(self, path=None):
        if path is not None:
            self.read_pkg_file(open(path))
        else:
            self.name = None
            self.version = None
            self.author = None
            self.author_email = None
            self.maintainer = None
            self.maintainer_email = None
            self.url = None
            self.license = None
            self.description = None
            self.long_description = None
            self.keywords = None
            self.platforms = None
            self.classifiers = None
            self.download_url = None
            # PEP 314
            self.provides = None
            self.requires = None
            self.obsoletes = None

    def read_pkg_file(self, file):
        """Reads the metadata values from a file object."""
        msg = message_from_file(file)

        def _read_field(name):
            value = msg[name]
            if value == 'UNKNOWN':
                return None
            return value

        def _read_list(name):
            values = msg.get_all(name, None)
            if values == []:
                return None
            return values

        metadata_version = msg['metadata-version']
        self.name = _read_field('name')
        self.version = _read_field('version')
        self.description = _read_field('summary')
        # we are filling author only.
        self.author = _read_field('author')
        self.maintainer = None
        self.author_email = _read_field('author-email')
        self.maintainer_email = None
        self.url = _read_field('home-page')
        self.license = _read_field('license')

        if 'download-url' in msg:
            self.download_url = _read_field('download-url')
        else:
            self.download_url = None

        self.long_description = _read_field('description')
        self.description = _read_field('summary')

        if 'keywords' in msg:
            self.keywords = _read_field('keywords').split(',')

        self.platforms = _read_list('platform')
        self.classifiers = _read_list('classifier')

        # PEP 314 - these fields only exist in 1.1
        if metadata_version == '1.1':
            self.requires = _read_list('requires')
            self.provides = _read_list('provides')
            self.obsoletes = _read_list('obsoletes')
        else:
            self.requires = None
            self.provides = None
            self.obsoletes = None

    def write_pkg_info(self, base_dir):
        """Write the PKG-INFO file into the release tree.
        """
        pkg_info = open( os.path.join(base_dir, 'PKG-INFO'), 'w')
        self.write_pkg_file(pkg_info)
        pkg_info.close()

    def write_pkg_file(self, file):
        """Write the PKG-INFO format data to a file object.
        """
        version = '1.0'
        if self.provides or self.requires or self.obsoletes:
            version = '1.1'

        self._write_field(file, 'Metadata-Version', version)
        self._write_field(file, 'Name', self.get_name())
        self._write_field(file, 'Version', self.get_version())
        self._write_field(file, 'Summary', self.get_description())
        self._write_field(file, 'Home-page', self.get_url())
        self._write_field(file, 'Author', self.get_contact())
        self._write_field(file, 'Author-email', self.get_contact_email())
        self._write_field(file, 'License', self.get_license())
        if self.download_url:
            self._write_field(file, 'Download-URL', self.download_url)

        long_desc = rfc822_escape(self.get_long_description())
        self._write_field(file, 'Description', long_desc)

        keywords = ','.join(self.get_keywords())
        if keywords:
            self._write_field(file, 'Keywords', keywords)

        self._write_list(file, 'Platform', self.get_platforms())
        self._write_list(file, 'Classifier', self.get_classifiers())

        # PEP 314
        self._write_list(file, 'Requires', self.get_requires())
        self._write_list(file, 'Provides', self.get_provides())
        self._write_list(file, 'Obsoletes', self.get_obsoletes())

    def _write_field(self, file, name, value):
        file.write('%s: %s\n' % (name, self._encode_field(value)))

    def _write_list (self, file, name, values):
        for value in values:
            self._write_field(file, name, value)

    def _encode_field(self, value):
        if value is None:
            return None
        if isinstance(value, unicode):
            return value.encode(PKG_INFO_ENCODING)
        return str(value)

    # -- Metadata query methods ----------------------------------------

    def get_name(self):
        return self.name or "UNKNOWN"

    def get_version(self):
        return self.version or "0.0.0"

    def get_fullname(self):
        return "%s-%s" % (self.get_name(), self.get_version())

    def get_author(self):
        return self._encode_field(self.author) or "UNKNOWN"

    def get_author_email(self):
        return self.author_email or "UNKNOWN"

    def get_maintainer(self):
        return self._encode_field(self.maintainer) or "UNKNOWN"

    def get_maintainer_email(self):
        return self.maintainer_email or "UNKNOWN"

    def get_contact(self):
        return (self._encode_field(self.maintainer) or
                self._encode_field(self.author) or "UNKNOWN")

    def get_contact_email(self):
        return self.maintainer_email or self.author_email or "UNKNOWN"

    def get_url(self):
        return self.url or "UNKNOWN"

    def get_license(self):
        return self.license or "UNKNOWN"
    get_licence = get_license

    def get_description(self):
        return self._encode_field(self.description) or "UNKNOWN"

    def get_long_description(self):
        return self._encode_field(self.long_description) or "UNKNOWN"

    def get_keywords(self):
        return self.keywords or []

    def get_platforms(self):
        return self.platforms or ["UNKNOWN"]

    def get_classifiers(self):
        return self.classifiers or []

    def get_download_url(self):
        return self.download_url or "UNKNOWN"

    # PEP 314
    def get_requires(self):
        return self.requires or []

    def set_requires(self, value):
        import distutils2.versionpredicate
        for v in value:
            distutils2.versionpredicate.VersionPredicate(v)
        self.requires = value

    def get_provides(self):
        return self.provides or []

    def set_provides(self, value):
        value = [v.strip() for v in value]
        for v in value:
            import distutils2.versionpredicate
            distutils2.versionpredicate.split_provision(v)
        self.provides = value

    def get_obsoletes(self):
        return self.obsoletes or []

    def set_obsoletes(self, value):
        import distutils2.versionpredicate
        for v in value:
            distutils2.versionpredicate.VersionPredicate(v)
        self.obsoletes = value


#
# micro-language for PEP 345 environment markers
#
class _Operation(object):

    # restricted set of names
    names = {'sys.platform': sys.platform,
             'python_version': '%s.%s' % (sys.version_info[0],
                                          sys.version_info[1]),
             'python_full_version': sys.version.split()[0],
             'os.name': os.name,
             'platform.version': platform.version,
             'platform.machine': platform.machine}

    # allowed operators
    ops = {'==': 'op_equal'}

    def __init__(self):
        self.left = None
        self.op = None
        self.right = None

    def __repr__(self):
        return '%s %s %s' % (self.left, self.op, self.right)

    def op_equal(self, left, right):
        return left == right

    def _is_string(self, value):
        # XXX need to add " as well
        return value.startswith("'") and value.endswith("'")

    def _convert(self, value):
        if value in self.names:
            return self.names[value]
        return value

    def _check_name(self, value):
        if value not in self.names:
            raise TypeError('Not supported "%s"' % value)

    def __call__(self):
        if self._is_string(self.left):
            self.left = self.left.strip("'")
            if self._is_string(self.right):
                raise TypeError('Cannot compare two strings')
            else:
                self._check_name(self.right)
        else:
            if self._is_string(self.right):
                self.right = self.right.strip("'")
                self._check_name(self.left)
            else:
                raise TypeError('Cannot compare two strings')

        if self.op not in self.ops:
            raise TypeError('Operator not supported "%s"' % self.op)

        left = self._convert(self.left)
        right = self._convert(self.right)
        return getattr(self, self.ops[self.op])(left, right)

class _OR(object):
    def __init__(self, left, right=None):
        self.left = left
        self.right = right

    def filled(self):
        return self.right is not None

    def __repr__(self):
        return 'OR(%s, %s)' % (repr(self.left), repr(self.right))

    def __call__(self):
        return self.left() or self.right()


class _AND(object):
    def __init__(self, left, right=None):
        self.left = left
        self.right = right

    def filled(self):
        return self.right is not None

    def __repr__(self):
        return 'AND(%s, %s)' % (repr(self.left), repr(self.right))

    def __call__(self):
        return self.left() and self.right()

class _CHAIN(object):

    def __init__(self):
        self.ops = []
        self.op_starting = True

    def eat(self, toktype, tokval, rowcol, line, logical_line):
        if toktype not in (NAME, OP, STRING, ENDMARKER):
            raise TypeError('Not supported %s' % line)

        if self.op_starting:
            op = _Operation()
            if len(self.ops) > 0:
                last = self.ops[-1]
                if isinstance(last, (_OR, _AND)) and not last.filled():
                    last.right = op
                else:
                    self.ops.append(op)
            else:
                self.ops.append(op)
            self.op_starting = False
        else:
            op = self.ops[-1]

        if (toktype == ENDMARKER or
            (toktype == NAME and tokval in ('and', 'or'))):
            if toktype == NAME and tokval == 'and':
                self.ops.append(_AND(self.ops.pop()))
            elif toktype == NAME and tokval == 'or':
                self.ops.append(_OR(self.ops.pop()))
            self.op_starting = True
            return

        if isinstance(op, (_OR, _AND)) and op.right is not None:
            op = op.right

        if toktype in (NAME, STRING) or (toktype == OP and tokval == '.'):
            if op.op is None:
                if op.left is None:
                    op.left = tokval
                else:
                    op.left += tokval
            else:
                if op.right is None:
                    op.right = tokval
                else:
                    op.right += tokval
        elif toktype == OP:
            op.op = tokval

    def result(self):
        for op in self.ops:
            if not op():
                return False
        return True

def _interpret(marker):
    """Interprets a marker and return a result given the environment."""
    operations = _CHAIN()
    tokenize(StringIO(marker).readline, operations.eat)
    return operations.result()

