# This module contains replacements for PIP's vcs backends.  These
# replacements add two capabilities: 
#
# 1. get_remote_refs(), which pulls symbolic (branch and tag)
#    references out of a remote repostory and interprets them as
#    version numbers.
#
# 2. unpack() adds the ability to produce a working copy at a
#    particular revision
#
# For now, only Git is supported, but in principle we could make some
# other backends work too.  Mercurial is apparently a problem because
# there's no way to implement get_remote_refs without cloning the
# whole repository locally.
