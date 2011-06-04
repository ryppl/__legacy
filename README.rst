.. title:: Ryppl - Git-based Software Development / Testing / Installation

================================================================
A Git-based Software Development / Testing / Installation System
================================================================

.. image:: http://ryppl.github.com/_static/ryppl.png
   :align: right

-----------------
The Ryppl Concept
-----------------

Ryppl is a distributed cross-platform software management system
designed to accommodate both end-users and developers. Ryppl unites
version control, test management, package management, release
management, reporting, and other sub-systems into a coherent and
scalable software management system.

Unlike a traditional package manager, which only delivers binaries
and/or a source snapshot, when ryppl downloads a package, it can give
you a clone of a Git repository, with that package’s entire
development history. If you’re an ordinary end-user, the fact that
it’s a git repository may be invisible to you, but if you’re a
developer, it means you’re already prepared to work on the package,
keep track of your changes, and submit them to the official
maintainer(s).

Ryppl includes facilities for building, testing, and installing
packages on the local machine. However, it also has integrated support
for remote testing. That is, you can arrange that tests be run on
build slaves located “out there” on the internet. Remote testing allows
developers to discover portability issues without having direct access
to every build platform.

---------------
This Repository
---------------

The project is very active and making progress, but has evolved
considerably, and this repository no longer has any useful code in it.
You can explore the `old-master
<https://github.com/ryppl/ryppl/tree/old-master>`_ branch to find code
and docs that may be relevant.  We're trying to keep the useful
documentation together at `ryppl.org <http://ryppl.org>`_.

---------
Resources
---------

News, Project Status: http://ryppl.org
Repositories: http://github.com/ryppl
