======================
PyCon packaging sprint
======================

.. contents::

We sprinted on Distutils2 at the US Pycon 2010 sessions.  This is one
of the results of that work.

Distutils is used by both developers and packagers.

:developers: People who write code in python.  The code may be
    distributed as an sdist or a variety of binary versions.  The
    developer presently uses setup.py to tell distutils how to build
    the sdist and binary packages.
:packagers: People who package sdists into binary packages for a Linux
    distribution. (Is there an equivalent role for people who make
    Windows binary packages? Or do developers generally do that for
    their own packages?)

----------------------
Problems for packagers
----------------------

We identified specific problems packagers face when creating deb/rpm:

The problem this document is intended to solve: **want to lay out files across the filesystem in a FHS-compliant way**

Problems that are fixed simply by not using setuptools:

- get rid of ez_setup.py

- breakages using ez_setup => Some setup.py scripts import ez_setup.
  ez_setup requires a specific version of setuptools but doesn't
  actually need it -- lesser versions work fine.

Problems that are out of scope, at least for now:

- Requires that are for a specific version (or range) because of bugs
  (not API change/features) but the distro packages have backported
  the fixes needed to an earlier version:

- differences between distribution names of packages e.g. "what are
  the packages of NumPy called?"

- Egg version (specified in a Require section in setup.py) doesn't
  match the distro package version
  https://www.redhat.com/archives/fedora-python-devel-list/2008-June/msg00002.html

We want to solve these issues for Linux distribution packages without
negatively impacting Windows, OS X, or pure-python
(i.e. easy_install/pip/virtualenv) installs.

Example problem with current distutils
======================================

In
http://docs.python.org/distutils/setupscript.html#installing-additional-files
there is this example of supplying an initscript within a setup.py::

    setup(...,
          data_files=[('bitmaps', ['bm/b1.gif', 'bm/b2.gif']),
                      ('config', ['cfg/data.cfg']),
                      ('/etc/init.d', ['init-script'])]
         )

This suffers from several problems:

1. The file hardcodes "/etc/init.d" as the directory for installation
   of the initscript.  However, this varies between different Linux
   distributions.  The above example assumes SysV init, but isn't
   correct for systems using Upstart (the initscripts are likely to
   need to be different for this case).  Even within systems using
   SysV init, the content of the script can vary between different
   distributions

2. The FHS mandates that configuration files go below /etc, but on a
   Windows box that's meaningless.

3. The file is a python script: if we want to extract data from it, we
   have to either run it, or somehow parse it; we would need to
   sandbox.  We would prefer a declarative minilanguage for specifying
   this data.

Similarly: documentation files, .h files (e.g. NumPy)

We want a system that:

1. is easy for developers, does not require an "install" or "build"
   phase during the edit/test development loop in a working copy

2. supports both FHS-compliant scattering across the filesystem
   hierarchy, and Windows, and virtualenv-style trees.

-----------------------
Problems for Developers
-----------------------

Package/file lists in multiple places
=====================================

* MANIFEST
* MANIFEST.in
* setup.py::data_files
* setup.py::package_data
* setup.py::packages
* setup.py::scripts

Replace all of these with settings in ``setup.cfg`` to specify runtime
files (python code, resource files) and files that belong in the sdist
but are not wanted for runtime.

No idea where Linux distros want files
======================================

Sometimes programmers want to do the right thing for people wanting to
package their programs in Linux distributions, but they don't know
where they belong.  Making matters worse, the files can go in
different places on different Linux distributions or on Windows and
MacOS.  Placing the files in the wrong place can lead to errors at
runtime, for instance, if the file needs to be writable by the module
but it's placed on a read-only filesystem.

This PEP attempts to deal with this by categorizing files so
developers can properly mark what properties their files need and
using an API to access the files, abstracting the different file
locations on different platforms.

Hard to extend the build commands
=================================

* distutils documentation is very poor

* distutils build commands are classes with special method names --
  why not simple functions?

* how do you extend the data allowed to be set in entries setup()?

* build commands sometimes need to act on the same arguments.  No way
  to pass these between them right now.


-----------------------------------
Proposed solution for placing files
-----------------------------------

This solution attempts to make several pieces of building and
installing better.  It merges the many file lists into a single file,
simplifies (or eliminates the need for) setup.py, and allows packagers
to place resource files in locations appropriate to their
distribution.

This solution comes in three pieces:

1. A ``resources`` section in ``setup.cfg`` that maps resource files
   to their categories (and optionally subdirectory prefixes within
   those categories)

2. A ``sysconfig.cfg`` file at the system Python level that maps
   categories to a position on the filesystem

3. A simple ``pkgutil.open()`` API to access resources from code

Rationale
=========

1. The evidence (from ``__file__`` usage) is strong that package devs
   want to think in terms of paths within their local dev tree. They
   don't want to worry about categorizing or finding their static
   files elsewhere.

2. Package devs are more likely to use an API that makes them think
   less and type less.

3. Package devs are more likely to accept patches from packagers if
   that patch only touches a single .cfg file, rather than touching
   every single ``pkgutil.open()`` call throughout their code.

Therefore, the ``pkgutil.open()`` call should accept a simple path
relative to the package/distribution root. The ``resources`` section
in ``setup.cfg`` uses globs to categorize those files:
forward-thinking package devs can write this section, or packagers can
do it for them and submit patches.


"resources" section in setup.cfg
================================

The setup.py file has many sections that need to list files. We plan
to remove those lists to ``setup.cfg``. The ``resources`` section of
``setup.cfg`` replaces the current ``package_data``, ``data_files``,
and ``extra_files`` options in ``setup.py``.

There are three pieces of information that are needed for resource
files:

1. Position in the source tree
   (e.g. 'mailman/database/schemas/schema.cfg', 'mywidget/jquery.js')

* Position when installed
  (e.g. '/etc/mailman/database/schemas/schema.cfg',
  '/usr/share/mywidget-1.1/javascript/jquery.js'). For simple
  virtualenv-style installations, this may well be the same as (1).

* Key used when referencing the resource from code. Ideally, this
  could be the same as (1), but because of difficulties in finding
  "distribution root" at runtime from a ``pkgutil.open()`` call, it
  will instead have to be a combination of "module name" and "path
  relative to module", similar to what ``pkg_resources`` does.

The information that the developer is concerned with:
* Position in the source tree
* Key used in referencing it

The information the downstream packager (rpm/deb/sysadmin) cares about are:
* Position when installed
* Key used in referencing it

Example
-------

We have a source tree with the following files::

  mailman-1.0/
    README
    some.tpl
    some-new-semantic.sns
    mailman/
      database/
        mailman.db
        schemas/
          blah.schema
      etc/
        my.cnf
      foo/
        some/
          path/
            bar/
              my.cfg
            other.cfg
    developer-docs/
      index.txt
      api/
        toc.txt

Here's where we want the files to end up in a typical Linux distribution:

==  ====================================  ===================================================================================================
##  Relative path in source tree          Final full installed path
==  ====================================  ===================================================================================================
1   mailman/database/schemas/blah.schema  /var/mailman/schemas/blah.schema
2   some.tpl                              /var/mailman/templates/some.tpl
3   path/to/some.tpl                      /var/mailman/templates/path/to/some.tpl
4   mailman/database/mailman.db           /var/mailman/database/mailman.db
5   developer-docs/index.txt              /usr/share/doc/mailman/developer-docs/index.txt
6   developer-docs/api/toc.txt            /usr/share/doc/mailman/developer-docs/api/toc.txt
7   README                                /usr/share/doc/mailman/README
8   mailman/etc/my.cnf                    /etc/mailman/my.cnf
9   mailman/foo/some/path/bar/my.cfg      /etc/mailman/baz/some/path/bar/my.cfg AND
                                          /etc/mailman/hmm/some/path/bar/my.cfg + 
                                          emit a warning
10  mailman/foo/some/path/other.cfg       /etc/mailman/some/path/other.cfg
11  some-new-semantic.sns                 /var/funky/mailman/some-new-semantic.sns
==  ====================================  ===================================================================================================

The numbers in the above placements are referenced below.

setup.cfg
~~~~~~~~~

The setup.cfg file allows the developer and/or packager to mark what
categories the files belong to.  These are drawn from the types of
files that the FHS and GNU coding standards define::

  [resources]
  # path glob                   category                placement from above table

  mailman/database/schemas/*  = {appdata}/schemas          # 1
  **/*.tpl                    = {appdata}/templates        # 2, 3  # does NOT flatten folder structure in destination
  developer-docs/**/*.txt     = {doc}                   # 5, 6
  README                      = {doc}                   # 7
  mailman/etc/*               = {config}                # 8
  mailman/foo/**/bar/*.cfg    = {config}/baz            # 9
  mailman/foo/**/*.cfg        = {config}/hmm            # 9, 10
  some-new-semantic.txt       = {funky-crazy-category}  # 11

The glob definitions are relative paths that match files from the top
of the source tree (the location of ``setup.cfg``). Forward slashes
(only) are used as path separator.

:"*": is a glob that matches any characters within a file or directory
name
:"**": is a recursive glob that matches any characters within a file
or directory name as well as a forward slash (thus an arbitrarily deep
number of directories)

The "category" value both categorizes the files and allows for placing
them in a more fine-grained subdirectory within a category. This value
must begin with a {category}; raw absolute or relative paths are not
allowed.

The full Python 3 string interpolation language is not supported, only
simple {category} substitutions. The {category} is looked up in a
system-level Python ``sysconfig.cfg`` file, where operating system
vendors and system administrators can define where in the filesystem
various types of files are placed. The category paths will generally
include a {distribution.name} variable, to isolate one package's files
of a given type from other packages.

As can be seen from the examples above, explicitly-matched directory
prefixes are stripped from the relative path before it is appended to
the category location. Glob matches are never stripped (to avoid
flattening hierarchies and overwriting files). In the
``mailman/foo/\*\*/\*.cfg`` example, ``mailman/foo`` is removed, but
not any directories matched by the recursive glob: see entries 9 and
10 in the example table.

sysconfig.cfg
~~~~~~~~~~~~~

This is a system-wide Python configuration file (TODO: can be
overridden by e.g. virtualenv) that defines where on the filesystem
resources will actually be installed.  A sample ``sysconfig.cfg`` can
be found in the ``distutils2`` repository at
``src/distutils2/_backport/sysconfig.cfg`` [3].

Links

.. [1] Filesystem Hierarchy Standard http://www.pathname.com/fhs/
.. [2] Rationale from the FHS which makes the distinctions between parts of the filesystem: http://www.pathname.com/fhs/pub/fhs-2.3.html#THEFILESYSTEM
.. [3] sample sysconfig.cfg: http://bitbucket.org/tarek/distutils2/src/tip/src/distutils2/_backport/sysconfig.cfg

What happens?
~~~~~~~~~~~~~
As an example, ``mailman/database/schemas/blah.schema``:

1. The file ``mailman/database/schemas/blah.schema`` in the source
   tree matches ``mailman/database/schemas/*`` within the
   ``resources`` stanza of the setup.cfg, which has right-hand side
   ``{appdata}/schemas``

2. The ``*`` in the left-hand-side matches ``blah.schema``, and the
   initial ``mailman/database/schemas/`` is stripped, so the
   installation path for the file is mapped to
   ``{appdata}/schemas/blah.schema``

3. The label ``appdata`` is listed in the ``sysconfig.cfg`` section
   for the ``posix_prefix`` installation scheme as installed to
   ``/usr/share/{distribution.name}``.  This expands out to:
   ``/usr/share/mailman``

4. The result is that the source file
   ``mailman/database/schemas/blah.schema`` is installed to
   ``/var/mailman/schemas/blah.schema``, and this mapping is recorded
   in a RESOURCES file in the installation metadata for the
   distribution.

5. The source code can open the file at runtime via the API call
   ``pkgutil.open('mailman', 'database/schemas/blah.schema')`` (where
   the first argument is an importable Python package name, and the
   second is a path relative to the location of that package), and
   pkgutil will (using the RESOURCES mapping) open it from
   ``/var/mailman/schemas/blah.schema``.

6. If the package is not installed, and thus has no RESOURCES mapping,
   ``pkgutil.open('mailman',
   'database/schemas/blah.schema')``

1. The file `mailman/database/schemas/blah.schema` in the source tree matches `mailman/database/schemas/*` within the data clause of the setup.cfg, so it is treated as having the label `{data}`.
2. The clause specified a prefix path, so the installation path for the file is mapped to "schemas/blah.schema"
3. The label "data" is listed in the [resource_variables] stanza as being installed to "/var/mailman"
4. The result is that the source file "mailman/database/schemas/blah.schema" is installed within the rpm/deb to "/var/mailman/schemas/blah.schema"
5. The source code can still open the file via an API using pkgutil.open('mailman', 'database/schemas/blah.schema') and have the underlying system open it from "/var/mailman/schemas/blah.schema".


Advice to packagers for fixing file locations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are two places where you might need to change things in order to
customize the locations that files are installed into.  The setup.cfg file can
be patched if the files are miscategorized.  For instance someone marks a help
file that is used by the app at runtime as {doc} when it should be marked as
{help}.  These types of patches should be submitted to the upstream project.
The resource_variables file can be changed to define different locations for
all apps on a system.  This should usually be done once in a systemwide file
for the distribution.  Changing this again may require the system packager to
rebuild all their python modules to change the file location.  There is API in
pkgutils to allow adding categories to the resource_variables file from
a script that should be used instead of trying to edit the file with raw text
processing.

API
===

pkgutils.open
-------------

Returns a file object for the resource.

::

  pkgutils.open('STRING_NAME_FOR_PACKAGE', 'filename/with/path/relative/to/the/source/package/directory')
  Example:
  pkgutils.open('mailman', 'database/schemas/blah.schema')
  <open file '/usr/share/mailman/schemas/blah.schema', mode 'r' at 0x7f938e325d78>

* First argument is the string name for a python package.
* Second argument is the directory path relative to the python package's directory.
* At install (or build) time we create a metadata file that maps from the source tree files to the files in their installed locations on the filesystem.
* pkgutil.open() consults the metadata file to decide where to find the resource. If the metadata file is not found (as in a package before the egg is built), open()  falls back to traversing the given relative path starting from the root of the calling package (using __name__).
* pkgutil.open() calls from nested packages aren't a problem because, after all, we pass the desired 'module_name' to start from as the first arg.

* ? Do we still need this? Default behavior:  alongside the package files (if the real-installed-locations metadata file does not exist). Or if the package is installed without any resource_variables specified. ?</>?

pkgutils.filename
-----------------

Returns a resource's filename with the full path.

::

  pkgutils.filename('STRING_NAME_FOR_PACKAGE', 'filename/with/path/relative/to/the/source/package/directory')
  Example:
  pkgutils.filename('mailman', 'database/schemas/blah.schema')
  '/usr/share/mailman/schemas/blah.schema'

pkgutils.add_category
---------------------

Adds a new category to the resource variables filename.

::

  pkgutils.add_category('CATEGORY', 'LOCATION')
  Example:
  pkgutils.add_category('lockdir', '{statedir}/lock')

Using the API allows the parser to protect from adding duplicate categories.

----
Todo
----

These need to be worked in or discarded somehow

 * Differences between applications and packages
   - Applications sometimes want a private library (for instance to do their commandline parsing)

Ideally, for every resource file, the developer (or the defaults) have classified with a "label" *TODO*: we don't have a default classifier right now: for instance::

  **/*.txt = doc
  **/*.png = data
  **/*.jpg = data
  **/*.gif = data
  **/*.cfg = config


Similar to i18n: marking of strings for translatability: gives you an ID, and a default value
Analagous to gettext: parse the source, figure out the resources

[X] Per-distro (per site ?): label placement file, mapping labels to system locations *I think this is done*

[X] What strings are valid as labels? only strings that are valid Python 2 identifiers: ([_A-Za-z][_A-Za-z0-9]*)  TODO: doublecheck this! *Obsolete* We have gotten rid of the labels

[X] So now, when it comes to building a deb/rpm, we have another file: "label placement" which maps from labels to rules about placement on the filesystem, written once by each linux distribution: *I think this is done*



How Debian does a .install file
===============================

In `packagename.install`::

    etc/* etc
    usr/* usr
    Products/statusmessages/* usr/share/zope/Products/statusmessages3

Each line has 2 parts:
* A glob of the source path within the deb
* Where it should land within the fakeroot (which corresponds to the final installed path)

This gives the packager the opportunity to both move and rename things, and it's fairly concise.


Building different packages from one source
===========================================

?? Do we want to do this??

Use case
--------

Split the docs into a separate sdist from the code so that people can download them separately.
(Matthias)

Another use case
----------------

Need to split submodule into its own binary package (essentially converting top-level to a namespace package).



Alternate ways of specifying labels
-----------------------------------
Noufal's::

    [mailman]
    data = *.txt, README
    data.persistent = sqlite.db

----------------------

Tarek's::

    [files]

    data =
        mailman/database/schemas/*
        *.txt
        README

    data.persistent = sqlite.db

----------------------

Toshio's::

    [resources]
    *.jpg = data

Alternative Label Idea
======================

labels for different resource types:  images, manpages, script, config files etc, javascript, schema, sql, data files

(those labels impose some other issues - what would one do to differences in statically servable on a webserver versus gtkbuilder can find it)

pkg_resources already provides software with an API::

    pkg_resource.open(label='javascript', name='jquery.js')

Then we have the ability for Linux distros to place the different labels in FHS-compliant (or whatever) locations on the filesystem, mapping each label to a fs path::

    pkg_resource.open(label='config', name=')

    pkg_resource.resource_stream(pkgname='mailman', label='config', victim='schema.cfg')
    pkg_resource.resource_stream('mailman', 'mailman.config', 'schema.cfg')
    pkg_resource.resource_stream('mailman', 'mailman.config', 'schema.cfg', label='config')

analogy with logging:

- with logging: developer sets up streams of data; sysadmin decides what to do with each log stream
- with packaging: developer sets up streams of data; packaging system decides where to put each one

developer:

(1) everything's within my local working copy; look within it; want to be able to quickly hack on stuff without having to "install" somewhere, for fast edit/test loop
(2) "setup.py sdist" has given us a zipfile, put it on pypi, someone uses buildout on it
(3) as (2) but a distribution has moved things to FHS-compliant location


    pkgutil.open(pkgname='mailman.database.schemas', filename='schema.cfg') # <-- Does this work with our examples below?

    pkgutil.open(pkgname='mailman', label='data', filename='schemas/schema.cfg')

(It won't be easy to get package devs to use this API; __file__ feels less magic than some strange call from pkgutil. The simpler the API call and the more "builtin" it looks, the better.)

*TODO* Can we make sane defaults?  For instance, can pkgname default to the pkgname or modulename that the call is being made from?

*TODO* can we match things against a range of packages/paths

(1) ./mailman/config/schema.cfg
(2) .
(3) /etc/mailman/database/schemas/schema.cfg

mapping from labels to dirs::

  distro_dict = {
     'config':'/etc',
     'mandir':'/usr/share/mandir',
  }

Another old syntax proposal
===========================
::

    [resources]

    # data are composed of two elements
    #  1. the path relative to the package
    #  2. an optional prefix path that will replace the explicit (non-glob) initial path from (1)

    data =
        mailman/database/schemas/* schemas/
        **/*.tpl templates/

    data.persistent =
        mailman/database/mailman.db database/

    doc =
        developer-docs/**/*.txt
        README

    config =
        mailman/etc/* .           # all files in mailman/etc/* copied to
        mailman/foo/**/*.cfg foo  # all .cfg files below  mailman/foo/SOME/PATH/TO/FILE/ will get copied to foo/SOME/PATH/TO/FILE/
        mailman/foo/**/*.cfg
        mailman/foo/**/bar/*.cfg baz
