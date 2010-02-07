
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


Specifics of Setup
------------------

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

Now we'll look at a number of things that might happen.  A set of
changes to be applied will be referred to here as a “patch,” even if
not expressed or completely expressible as a patch file.

Developer Update
::::::::::::::::

Library developer releases a patch.  

Direct Developer Update
.......................

*libA* is patched.

* Patches must be classified so that users can choose which category
  of patches to apply automatically, e.g. “critical update,” “alpha,”
  “cosmetic,” “major version upgrade,” etc.

* Users must also be able to explicitly select patches to apply,
  preferably by name.

Indirect Developer Update
.........................

*libX* is patched.

User Update
:::::::::::

The developer of *proj* patches one of the libraries on which *proj*
depends.  Requirements:

* change will be checked into user's repo
* change persists there until merged upstream
* in the meantime developer can continue to update 
  all dependencies until there is no clean merge
* when there is no clean merge, several options are available:

  - revert
  - developer resolves merge.  **Question:** what happens to resulting
    patch?
  - *other options?*


Direct User Update
..................

User patches *libA*


Indirect User Update
....................

User patches *libX*

Upstream Merge
::::::::::::::

Library developer merges and releases a user update.

Direct Upstream Merge
.....................

*libA* is patched

Indirect Upstream Merge
.......................

*libX* is patched


