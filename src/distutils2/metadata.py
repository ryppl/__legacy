"""
Implementation of the Metadata for Python packages

Supports all Metadata formats (1.0, 1.1, 1.2).
"""

import re
import os
import sys
import platform
from StringIO import StringIO
from email import message_from_file
from tokenize import tokenize, NAME, OP, STRING, ENDMARKER

from distutils2.log import warn
from distutils2.util import rfc822_escape
from distutils2.version import (is_valid_predicate, is_valid_version,
                                is_valid_versions)
from distutils2.errors import (MetadataConflictError,
                               MetadataUnrecognizedVersionError)

try:
    # docutils is installed
    from docutils.utils import Reporter
    from docutils.parsers.rst import Parser
    from docutils import frontend
    from docutils import nodes
    from StringIO import StringIO

    class SilentReporter(Reporter):

        def __init__(self, source, report_level, halt_level, stream=None,
                     debug=0, encoding='ascii', error_handler='replace'):
            self.messages = []
            Reporter.__init__(self, source, report_level, halt_level, stream,
                              debug, encoding, error_handler)

        def system_message(self, level, message, *children, **kwargs):
            self.messages.append((level, message, children, kwargs))

    _HAS_DOCUTILS = True
except ImportError:
    # docutils is not installed
    _HAS_DOCUTILS = False

# public API of this module
__all__ = ('DistributionMetadata', 'PKG_INFO_ENCODING',
           'PKG_INFO_PREFERRED_VERSION')

# Encoding used for the PKG-INFO files
PKG_INFO_ENCODING = 'utf-8'

# preferred version. Hopefully will be changed
# to 1.2 once PEP 345 is supported everywhere
PKG_INFO_PREFERRED_VERSION = '1.0'

_LINE_PREFIX = re.compile('\n       \|')
_241_FIELDS = ('Metadata-Version',  'Name', 'Version', 'Platform',
               'Summary', 'Description',
               'Keywords', 'Home-page', 'Author', 'Author-email',
               'License')

_314_FIELDS = ('Metadata-Version',  'Name', 'Version', 'Platform',
               'Supported-Platform', 'Summary', 'Description',
               'Keywords', 'Home-page', 'Author', 'Author-email',
               'License', 'Classifier', 'Download-URL', 'Obsoletes',
               'Provides', 'Requires')

_314_MARKERS = ('Obsoletes', 'Provides', 'Requires')

_345_FIELDS = ('Metadata-Version',  'Name', 'Version', 'Platform',
               'Supported-Platform', 'Summary', 'Description',
               'Keywords', 'Home-page', 'Author', 'Author-email',
               'Maintainer', 'Maintainer-email', 'License',
               'Classifier', 'Download-URL', 'Obsoletes-Dist',
               'Project-URL', 'Provides-Dist', 'Requires-Dist',
               'Requires-Python', 'Requires-External')

_345_MARKERS = ('Provides-Dist', 'Requires-Dist', 'Requires-Python',
                'Obsoletes-Dist', 'Requires-External', 'Maintainer',
                'Maintainer-email', 'Project-URL')

_ALL_FIELDS = []

for field in _241_FIELDS + _314_FIELDS + _345_FIELDS:
    if field in _ALL_FIELDS:
        continue
    _ALL_FIELDS.append(field)

def _version2fieldlist(version):
    if version == '1.0':
        return _241_FIELDS
    elif version == '1.1':
        return _314_FIELDS
    elif version == '1.2':
        return _345_FIELDS
    raise MetadataUnrecognizedVersionError(version)

def _best_version(fields):
    """Will detect the best version depending on the fields used."""
    def _has_marker(keys, markers):
        for marker in markers:
            if marker in keys:
                return True
        return False
    keys = fields.keys()
    is_1_1 = _has_marker(keys, _314_MARKERS)
    is_1_2 = _has_marker(keys, _345_MARKERS)
    if is_1_1 and is_1_2:
        raise MetadataConflictError('You used both 1.1 and 1.2 fields')

    # we have the choice, either 1.0, or 1.2
    #   - 1.0 has a broken Summary field but work with all tools
    #   - 1.1 is to avoid
    #   - 1.2 fixes Summary but is not spreaded yet
    if not is_1_1 and not is_1_2:
        return PKG_INFO_PREFERRED_VERSION
    if is_1_1:
        return '1.1'
    return '1.2'

_ATTR2FIELD = {'metadata_version': 'Metadata-Version',
        'name': 'Name',
        'version': 'Version',
        'platform': 'Platform',
        'supported_platform': 'Supported-Platform',
        'summary': 'Summary',
        'description': 'Description',
        'keywords': 'Keywords',
        'home_page': 'Home-page',
        'author': 'Author',
        'author_email': 'Author-email',
        'maintainer': 'Maintainer',
        'maintainer_email': 'Maintainer-email',
        'licence': 'License',
        'classifier': 'Classifier',
        'download_url': 'Download-URL',
        'obsoletes_dist': 'Obsoletes-Dist',
        'provides_dist': 'Provides-Dist',
        'requires_dist': 'Requires-Dist',
        'requires_python': 'Requires-Python',
        'requires_external': 'Requires-External',
        'requires': 'Requires',
        'provides': 'Provides',
        'obsoletes': 'Obsoletes',
        'project_url': 'Project-URL',
        }

_PREDICATE_FIELDS = ('Requires-Dist', 'Obsoletes-Dist', 'Provides-Dist')
_VERSIONS_FIELDS = ('Requires-Python',)
_VERSION_FIELDS = ('Version',)
_LISTFIELDS = ('Platform', 'Classifier', 'Obsoletes',
        'Requires', 'Provides', 'Obsoletes-Dist',
        'Provides-Dist', 'Requires-Dist', 'Requires-External',
        'Project-URL')
_LISTTUPLEFIELDS = ('Project-URL',)

_ELEMENTSFIELD = ('Keywords',)

_UNICODEFIELDS = ('Author', 'Maintainer', 'Summary', 'Description')


class DistributionMetadata(object):
    """Distribution meta-data class (1.0 or 1.2).
    """
    def __init__(self, path=None, platform_dependant=False,
                 execution_context=None):
        self._fields = {}
        self.version = None
        self.docutils_support = _HAS_DOCUTILS
        self.platform_dependant = platform_dependant
        if path is not None:
            self.read(path)
        self.execution_context = execution_context

    def _set_best_version(self):
        self.version = _best_version(self._fields)
        self._fields['Metadata-Version'] = self.version

    def _write_field(self, file, name, value):
        file.write('%s: %s\n' % (name, value))

    def _write_list(self, file, name, values):
        for value in values:
            self._write_field(file, name, value)

    def _encode_field(self, value):
        if isinstance(value, unicode):
            return value.encode(PKG_INFO_ENCODING)
        return str(value)

    def __getitem__(self, name):
        return self.get(name)

    def __setitem__(self, name, value):
        return self.set(name, value)

    def __delitem__(self, name):
        del self._fields[name]
        self._set_best_version()

    def _convert_name(self, name):
        if name in _ALL_FIELDS:
            return name
        name = name.replace('-', '_').lower()
        if name in _ATTR2FIELD:
            return _ATTR2FIELD[name]
        return name

    def _default_value(self, name):
        if name in _LISTFIELDS + _ELEMENTSFIELD:
            return []
        return 'UNKNOWN'

    def _check_rst_data(self, data):
        """Returns warnings when the provided data doesn't compile."""
        source_path = StringIO()
        parser = Parser()
        settings = frontend.OptionParser().get_default_values()
        settings.tab_width = 4
        settings.pep_references = None
        settings.rfc_references = None
        reporter = SilentReporter(source_path,
                          settings.report_level,
                          settings.halt_level,
                          stream=settings.warning_stream,
                          debug=settings.debug,
                          encoding=settings.error_encoding,
                          error_handler=settings.error_encoding_error_handler)

        document = nodes.document(settings, reporter, source=source_path)
        document.note_source(source_path, -1)
        try:
            parser.parse(data, document)
        except AttributeError:
            reporter.messages.append((-1, 'Could not finish the parsing.',
                                      '', {}))

        return reporter.messages

    def _platform(self, value):
        if not self.platform_dependant or ';' not in value:
            return True, value
        value, marker = value.split(';')
        return _interpret(marker, self.execution_context), value

    def _remove_line_prefix(self, value):
        return _LINE_PREFIX.sub('\n', value)

    #
    # Public APIs
    #
    def get_fullname(self):
        return '%s-%s' % (self['Name'], self['Version'])

    def is_metadata_field(self, name):
        name = self._convert_name(name)
        return name in _ALL_FIELDS

    def read(self, filepath):
        self.read_file(open(filepath))

    def read_file(self, fileob):
        """Reads the metadata values from a file object."""
        msg = message_from_file(fileob)
        self.version = msg['metadata-version']

        for field in _version2fieldlist(self.version):
            if field in _LISTFIELDS:
                # we can have multiple lines
                values = msg.get_all(field)
                self.set(field, values)
            else:
                # single line
                value = msg[field]
                if value is not None:
                    self.set(field, value)

    def write(self, filepath):
        """Write the metadata fields into path.
        """
        pkg_info = open(filepath, 'w')
        try:
            self.write_file(pkg_info)
        finally:
            pkg_info.close()

    def write_file(self, fileobject):
        """Write the PKG-INFO format data to a file object.
        """
        self._set_best_version()
        for field in _version2fieldlist(self.version):
            values = self.get(field)
            if field in _ELEMENTSFIELD:
                self._write_field(fileobject, field, ','.join(values))
                continue
            if field not in _LISTFIELDS:
                if field == 'Description':
                    values = values.replace('\n', '\n       |')
                values = [values]

            for value in values:
                self._write_field(fileobject, field, value)

    def set(self, name, value):
        """Controls then sets a metadata field"""
        name = self._convert_name(name)

        if (name in _ELEMENTSFIELD + ('Platform',) and
            not isinstance(value, (list, tuple))):
            if isinstance(value, str):
                value = value.split(',')
            else:
                value = []
        elif (name in _LISTFIELDS and
            not isinstance(value, (list, tuple))):
            if isinstance(value, str):
                value = [value]
            else:
                value = None

        if name in _PREDICATE_FIELDS and value is not None:
            for v in value:
                # check that the values are valid predicates
                if not is_valid_predicate(v.split(';')[0]):
                    warn('"%s" is not a valid predicate' % v)
        elif name in _VERSIONS_FIELDS and value is not None:
            if not is_valid_versions(value):
                warn('"%s" is not a valid predicate' % value)
        elif name in _VERSION_FIELDS and value is not None:
            if not is_valid_version(value):
                warn('"%s" is not a valid version' % value)

        if name in _UNICODEFIELDS:
            value = self._encode_field(value)
            if name == 'Description':
                value = self._remove_line_prefix(value)

        self._fields[name] = value
        self._set_best_version()

    def get(self, name):
        """Gets a metadata field."""
        name = self._convert_name(name)
        if name not in self._fields:
            return self._default_value(name)
        if name in _UNICODEFIELDS:
            value = self._fields[name]
            return self._encode_field(value)
        elif name in _LISTFIELDS:
            value = self._fields[name]
            if value is None:
                return []
            res = []
            for val in value:
                valid, val = self._platform(val)
                if not valid:
                    continue
                if name not in _LISTTUPLEFIELDS:
                    res.append(self._encode_field(val))
                else:
                    # That's for Project-URL
                    res.append((self._encode_field(val[0]), val[1]))
            return res

        elif name in _ELEMENTSFIELD:
            valid, value = self._platform(self._fields[name])
            if not valid:
                return []
            if isinstance(value, str):
                return value.split(',')
        valid, value = self._platform(self._fields[name])
        if not valid:
            return None
        return value

    def check(self):
        """Checks if the metadata are compliant."""
        # XXX should check the versions (if the file was loaded)
        missing = []
        for attr in ('Name', 'Version', 'Home-page'):
            value = self[attr]
            if value == 'UNKNOWN':
                missing.append(attr)

        if _HAS_DOCUTILS:
            warnings = self._check_rst_data(self['Description'])
        else:
            warnings = []
        return missing, warnings

    def keys(self):
        return _version2fieldlist(self.version)

    def values(self):
        return [self[key] for key in self.keys()]

    def items(self):
        return [(key, self[key]) for key in self.keys()]


#
# micro-language for PEP 345 environment markers
#
_STR_LIMIT = "'\""

# allowed operators
_OPERATORS = {'==': lambda x, y: x == y,
              '!=': lambda x, y: x != y,
              '>': lambda x, y: x > y,
              '>=': lambda x, y: x >= y,
              '<': lambda x, y: x < y,
              '<=': lambda x, y: x <= y,
              'in': lambda x, y: x in y,
              'not in': lambda x, y: x not in y}

def _operate(operation, x, y):
    return _OPERATORS[operation](x, y)

# restricted set of variables
_VARS = {'sys.platform': sys.platform,
         'python_version': '%s.%s' % (sys.version_info[0],
                                      sys.version_info[1]),
         'python_full_version': sys.version.split()[0],
         'os.name': os.name,
         'platform.version': platform.version,
         'platform.machine': platform.machine}

class _Operation(object):

    def __init__(self, execution_context=None):
        self.left = None
        self.op = None
        self.right = None
        if execution_context is None:
            execution_context = {}
        self.execution_context = execution_context

    def _get_var(self, name):
        if name in self.execution_context:
            return self.execution_context[name]
        return _VARS[name]

    def __repr__(self):
        return '%s %s %s' % (self.left, self.op, self.right)

    def _is_string(self, value):
        if value is None or len(value) < 2:
            return False
        for delimiter in _STR_LIMIT:
            if value[0] == value[-1] == delimiter:
                return True
        return False

    def _is_name(self, value):
        return value in _VARS

    def _convert(self, value):
        if value in _VARS:
            return self._get_var(value)
        return value.strip(_STR_LIMIT)

    def _check_name(self, value):
        if value not in _VARS:
            raise NameError(value)

    def _nonsense_op(self):
        msg = 'This operation is not supported : "%s"' % str(self)
        raise SyntaxError(msg)

    def __call__(self):
        # make sure we do something useful
        if self._is_string(self.left):
            if self._is_string(self.right):
                self._nonsense_op()
            self._check_name(self.right)
        else:
            if not self._is_string(self.right):
                self._nonsense_op()
            self._check_name(self.left)

        if self.op not in _OPERATORS:
            raise TypeError('Operator not supported "%s"' % self.op)

        left = self._convert(self.left)
        right = self._convert(self.right)
        return _operate(self.op, left, right)

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

    def __init__(self, execution_context=None):
        self.ops = []
        self.op_starting = True
        self.execution_context = execution_context

    def eat(self, toktype, tokval, rowcol, line, logical_line):
        if toktype not in (NAME, OP, STRING, ENDMARKER):
            raise SyntaxError('Type not supported "%s"' % tokval)

        if self.op_starting:
            op = _Operation(self.execution_context)
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

        if ((toktype in (NAME, STRING) and tokval not in ('in', 'not'))
            or (toktype == OP and tokval == '.')):
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
        elif toktype == OP or tokval in ('in', 'not'):
            if tokval == 'in' and op.op == 'not':
                op.op = 'not in'
            else:
                op.op = tokval

    def result(self):
        for op in self.ops:
            if not op():
                return False
        return True

def _interpret(marker, execution_context=None):
    """Interprets a marker and return a result given the environment."""
    marker = marker.strip()
    operations = _CHAIN(execution_context)
    tokenize(StringIO(marker).readline, operations.eat)
    return operations.result()

