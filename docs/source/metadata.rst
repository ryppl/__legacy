========
Metadata
========

Distutils2 provides a :class:`DistributionMetadata` class that can read and 
write Metadata files. It also supports PEP 345 environment markers and
checks that version numbers provided in the fields are PEP 386 compatible
when required.


Supported formats
=================

The class can read and write Metadata v1.0 and v1.2 
files. When a v1.1 file is read, it is transformed into 1.0 or 1.2 depending
on the fields provided. 1.1 fields are ignored in that case.

XXX explain why

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

The fields that supports environment markers (XXX) can be automatically 
ignored if the object is instanciated using the ``platform_dependant`` option.
:class:`DistributionMetadata` will interpret in the case the markers and will
automatically remove the fields that are not compliant with the running 
environment. Here's an example under Mac OS X. The win32 dependency 
we saw earlier is ignored::

    >>> from distutils2.metadata import DistributionMetadata
    >>> metadata = DistributionMetadata('PKG-INFO', platform_dependant=True)
    >>> metadata['Requires-Dist']
    ['bar']


Writing metadata
================

XXX demonstrate here how version numbers are checked when a key is set.

