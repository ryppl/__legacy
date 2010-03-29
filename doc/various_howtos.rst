Various howtos and assorted notes
=================================

Synchronize actual submodule clones to contents of :file:`gitmodules`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Commit modifications to :file:`.gitmodules`, rm the entry from
:file:`.git/config`, *rm the submodule directory from src/* then
``submodule init`` and ``submodule update``.  

