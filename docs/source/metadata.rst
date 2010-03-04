========
Metadata
========

Distutils2 provides a :class:`DistributionMetadata` class that can read and
write Metadata files. This class is compatible with all versions of Metadata:

- 1.0 : PEP 241
- 1.1 : PEP 314
- 1.2 : PEP 345

The PEP 345 implementation supports the micro-language for the environment
markers, and displays warnings when versions that are supposed to be
PEP 386 are violating the scheme.


Reading metadata
================

The :class:`DistributionMetadata` class can be instanciated with the path of
the metadata file, and provides a dict-like interface to the values::

    >>> from distutils2.metadata import DistributionMetadata
    >>> metadata = DistributionMetadata('PKG-INFO')
    >>> metadata.keys()[:5]
    ('Metadata-Version', 'Name', 'Version', 'Platform', 'Supported-Platform')
    >>> metadata['Name']
    'CLVault'
    >>> metadata['Version']
    '0.5'
    >>> metadata['Requires-Dist']
    ["pywin32; sys.platform == 'win32'", "Sphinx"]

The fields that supports environment markers can be automatically ignored if
the object is instanciated using the ``platform_dependant`` option.
:class:`DistributionMetadata` will interpret in the case the markers and will
automatically remove the fields that are not compliant with the running
environment. Here's an example under Mac OS X. The win32 dependency
we saw earlier is ignored::

    >>> from distutils2.metadata import DistributionMetadata
    >>> metadata = DistributionMetadata('PKG-INFO', platform_dependant=True)
    >>> metadata['Requires-Dist']
    ['bar']

If you want to provide your own execution context, let's say to test the
Metadata under a particular environment that is not the current environment,
you can provide your own values in the ``execution_context`` option, which
is the dict that may contain one or more keys of the context the micro-language
expects.

Here's an example, simulating a win32 environment::

    >>> from distutils2.metadata import DistributionMetadata
    >>> context = {'sys.platform': 'win32'}
    >>> metadata = DistributionMetadata('PKG-INFO', platform_dependant=True,
    ...                                 execution_context=context)
    ...
    >>> metadata['Requires-Dist'] = ["pywin32; sys.platform == 'win32'",
    ...                              "Sphinx"]
    ...
    >>> metadata['Requires-Dist']
    ['pywin32', 'Sphinx']


Writing metadata
================

Writing metadata can be done using the ``write`` API::

    >>> metadata.write('/to/my/PKG-INFO')

The class will pick the best version for the metadata, depending on the values
provided. If all the values provided exists in all versions, teh class will
used :attr:`metadata.PKG_INFO_PREFERRED_VERSION`. It is set by default to 1.0.


Conflict checking and best version
==================================

Some fields in PEP 345 have to follow a version scheme in their versions
predicate. When the scheme is violated, a warning is emited::

    >>> from distutils2.metadata import DistributionMetadata
    >>> metadata = DistributionMetadata()
    >>> metadata['Requires-Dist'] = ['Funky (Groovie)']
    "Funky (Groovie)" is not a valid predicate
    >>> metadata['Requires-Dist'] = ['Funky (1.2)']



XXX talk about check()



