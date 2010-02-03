
.. highlight:: git_shell

High-Level Scenarios
====================

In this section we're trying to address the different situations that
need to be handled by this system, not just for library developers,
but for end-users, integrators, etc.

The Diamond
-----------

This configuration of dependencies should be enough to uncover many of the edge cases.

.. digraph:: lib_dependencies

   "libA" -> "libC"
   "libA" -> "libX"
   "libB" -> "libX"
   "libB" -> "libD"
   "proj" -> "libA"
   "proj" -> "libB"
   
*proj* is a project that might not be hosted at ryppl. *libA*, *libB*,
*libC*, *libD*, and *libX* are ryppl library projects.


Set Up Specifics
----------------

The developer of *libA* has a .ryppl file to his project at the top level::

  depends libX:1.0-2.2,3.1
  depends libC

This specifies a dependency on a version of libX numbered 1.0 through
2.2 or numbered 3.1.  

.. Note:: We will need a rule for decoding and comparing version
   names/numbers.  Likely it will need to cover more complicated
   versions like 1.1b2, etc.

*libB* has a similar .ryppl file::

  depends libX:2.0-2.5,3.0 libD

The person developing *proj* does:

::

  ~/proj% ryppl get libA libB

This will pull down the latest release of *libA*, *libB*, *libC* and
*libD*, and version 2.2 of *libX*, since it's the latest version
compatible with both the latest *libA* and *libB*.

Alternatively, the developer of *proj* can have his own .ryppl file::

  depends libA libB

and simply execute::

  ~/proj% ryppl

.. admonition:: Question

   In a case like this one, if the latest *libA* and *libB* are not
   compatible with any common version of *libX*, what should happen?

   * Error?
   * Warning?
   * Look for earlier versions of *libA* and *libB* that are compatible?
   * Fall back to a guess about a compatible *libX*?

Events
------

Now we'll look at a number of things that might happen.
