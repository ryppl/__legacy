.. title:: Ryppl - Git-based Software Development / Testing / Installation

A Git-based Software Development / Testing / Installation System
================================================================

.. image:: http://www.ryppl.org/_static/ryppl.png
   :align: right

For emergent HTML documentation, see http://www.ryppl.org



Building The Docs
-----------------

Prerequisites
.............

* Python_
* Sphinx_
* GraphViz_
* `GNU Make`_

To build the documentation, enter the ``doc/`` subdirectory and issue
the command::

  $ make html

The results will be generated in the ``build/html/`` subdirectory of
this project.  If you don't like building in your source tree, you can
change the parent of the generated ``html/`` directory by setting the
make (or environment) variable ``BUILDDIR``::

  $ make BUILDDIR=/tmp/ryppl-build

.. _Python: http://python.org
.. _Sphinx: http://sphinx.pocoo.org/
.. _GNU Make: http://www.gnu.org/software/make/
.. _GraphViz: http://graphviz.org
