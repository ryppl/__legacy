#
## test_pypi_versions.py
##
##  A very simple test to see what percentage of the current pypi packages
##  have versions that can be converted automatically by distutils' new
##  suggest_normalized_version() into PEP-386 compatible versions.
##
##  Requires : Python 2.5+
##
##  Written by: ssteinerX@gmail.com
#

try:
   import cPickle as pickle
except:
   import pickle

import xmlrpclib
import os.path
import unittest2

from distutils2.version import suggest_normalized_version

def test_pypi():
    #
    ## To re-run from scratch, just delete these two .pkl files
    #
    INDEX_PICKLE_FILE = 'pypi-index.pkl'
    VERSION_PICKLE_FILE = 'pypi-version.pkl'

    package_info = version_info = []

    #
    ## if there's a saved version of the package list
    ##      restore it
    ## else:
    ##      pull the list down from pypi
    ##      save a pickled version of it
    #
    if os.path.exists(INDEX_PICKLE_FILE):
        print "Loading saved pypi data..."
        f = open(INDEX_PICKLE_FILE, 'rb')
        try:
            package_info = pickle.load(f)
        finally:
            f.close()
    else:
        print "Retrieving pypi packages..."
        server = xmlrpclib.Server('http://pypi.python.org/pypi')
        package_info  = server.search({'name': ''})

        print "Saving package info..."
        f = open(INDEX_PICKLE_FILE, 'wb')
        try:
            pickle.dump(package_info, o)
        finally:
            f.close()

    #
    ## If there's a saved list of the versions from the packages
    ##      restore it
    ## else
    ##     extract versions from the package list
    ##     save a pickled version of it
    #
    versions = []
    if os.path.exists(VERSION_PICKLE_FILE):
        print "Loading saved version info..."
        f = open(VERSION_PICKLE_FILE, 'rb')
        try:
            versions = pickle.load(f)
        finally:
            f.close()
    else:
        print "Extracting and saving version info..."
        versions = [p['version'] for p in package_info]
        o = open(VERSION_PICKLE_FILE, 'wb')
        try:
            pickle.dump(versions, o)
        finally:
            o.close()

    total_versions = len(versions)
    matches = 0.00
    no_sugg = 0.00
    have_sugg = 0.00

    suggs = []
    no_suggs = []

    for ver in versions:
        sugg = suggest_normalized_version(ver)
        if sugg == ver:
            matches += 1
        elif sugg == None:
            no_sugg += 1
            no_suggs.append(ver)
        else:
            have_sugg += 1
            suggs.append((ver, sugg))

    pct = "(%2.2f%%)"
    print "Results:"
    print "--------"
    print ""
    print "Suggestions"
    print "-----------"
    print ""
    for ver, sugg in suggs:
        print "%s -> %s" % (ver, sugg)
    print ""
    print "No suggestions"
    print "--------------"
    for ver in no_suggs:
        print ver
    print ""
    print "Summary:"
    print "--------"
    print "Total Packages  : ", total_versions
    print "Already Match   : ", matches, pct % (matches/total_versions*100,)
    print "Have Suggestion : ", have_sugg, pct % (have_sugg/total_versions*100,)
    print "No Suggestion   : ", no_sugg, pct % (no_sugg/total_versions*100,)

class TestPyPI(unittest2.TestCase):
    pass

def test_suite():
    return unittest2.makeSuite(TestPyPI)

if __name__ == '__main__':
    run_unittest(test_suite())

