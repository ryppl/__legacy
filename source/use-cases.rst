
.. highlight:: git_shell

Use Cases
=========

In this section we're trying to enumerate cases that need to be
handled by this system, not just for library developers, but for
end-users, integrators, etc.  These use cases are not currently
prioritized.  We divide them by the role of the initiator.

User
----

* I wanna get (and test) these three Boost libs (and whatever they depend on)
* I wanna hack on a Boost library
  * I wanna test a library (as released)
  * I wanna test my own version of the library
* I wanna develop a new Boost library

* Release Mgr:
  * I wanna tag a release of Boost
  * I want whole Boost regression tests

* I wanna send my patch to the maintainer

* I wanna contribute testing resources
  * subset of libraries
  * subset of possible developers/public repos
  * ...


Missing
-------

* Dependency Management - probably independent from CMake
* Testing is busted?  Yes, for Python.
* Testing is unweildy (having to call ctest)

* if we want to use CDash, makes sense to have CTest run tests.
  Incremental testing needs research in that case.


Beman Notes
-----------

Release Mgr
:::::::::::

* Releasability overview (email)
* Automatically notify maintainers of breakage (email).  Show test /failures/
* Auto-tagged releasable branch for each library
* Continuous testing of the release branch
* Make binaries

Developer
:::::::::

* XML Markup and maintainer stored per-library
* Request speculative testing
  * platform/branch specificity
  * auto-notification of results

Tester
::::::

* Dead simple slave sign-on
* Incremental testing

User
::::

* Summary of releasability criteria for a library.
