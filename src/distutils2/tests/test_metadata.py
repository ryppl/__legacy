"""Tests for distutils.command.bdist."""
import unittest2
import os
import sys

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

def test_suite():
    return unittest2.makeSuite(DistributionMetadataTestCase)

if __name__ == '__main__':
    run_unittest(test_suite())
