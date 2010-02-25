"""Tests for distutils.command.bdist."""
import unittest2
import os
import sys
from StringIO import StringIO

from distutils2.metadata import DistributionMetadata, _interpret

class DistributionMetadataTestCase(unittest2.TestCase):


    def test_interpret(self):
        platform = sys.platform
        version = sys.version.split()[0]
        os_name = os.name

        assert _interpret("sys.platform == '%s'" % platform)
        assert _interpret("sys.platform == '%s' or python_version == '2.4'" \
                % platform)
        assert _interpret("sys.platform == '%s' and "
                          "python_full_version == '%s'"\
                % (platform, version))
        assert _interpret("'%s' == sys.platform" % platform)

        assert _interpret('os.name == "%s"' % os_name)

        # stuff that need to raise a syntax error
        ops = ('os.name == os.name', 'os.name == 2', "'2' == '2'",
               'okpjonon', '', 'os.name ==')
        for op in ops:
            self.assertRaises(SyntaxError, _interpret, op)

        # combined operations
        OP = 'os.name == "%s"' % os_name
        AND = ' and '
        OR = ' or '
        assert _interpret(OP+AND+OP)
        assert _interpret(OP+AND+OP+AND+OP)
        assert _interpret(OP+OR+OP)
        assert _interpret(OP+OR+OP+OR+OP)

        # other operators
        assert _interpret("os.name != 'buuuu'")
        assert _interpret("python_version > '1.0'")
        assert _interpret("python_version < '5.0'")
        assert _interpret("python_version <= '5.0'")
        assert _interpret("python_version >= '1.0'")
        assert _interpret("'%s' in os.name" % os_name)
        assert _interpret("'buuuu' not in os.name")
        assert _interpret("'buuuu' not in os.name and '%s' in os.name" \
                            % os_name)


    def test_metadata_read_write(self):

        PKG_INFO = os.path.join(os.path.dirname(__file__), 'PKG-INFO')
        metadata = DistributionMetadata(PKG_INFO)
        res = StringIO()
        metadata.write_file(res)
        res.seek(0)
        res = res.read()
        f = open(PKG_INFO)
        wanted = f.read()
        self.assert_('Keywords: keyring,password,crypt' in res)
        f.close()

    def test_metadata_markers(self):
        # see if we can be platform-aware
        PKG_INFO = os.path.join(os.path.dirname(__file__), 'PKG-INFO')
        content = open(PKG_INFO).read()
        content = content % sys.platform
        metadata = DistributionMetadata(platform_dependant=True)
        metadata.read_file(StringIO(content))
        self.assertEquals(metadata['Requires-Dist'], ['bar'])

def test_suite():
    return unittest2.makeSuite(DistributionMetadataTestCase)

if __name__ == '__main__':
    run_unittest(test_suite())
