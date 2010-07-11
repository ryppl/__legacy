import os, sys, getopt, stat, pickle
from subprocess import PIPE, Popen

boost_manifest_pkl = 'boost-live-manifest.pkl'
verbose = False

# Print the usage message (there's probably a nifty python way to do this)
def usage():
    print '''Usage: findmoddiffs.py [-h] [-a] [-v] [--live-boost-repo=<dir>]
    -h                  : help
    -v                  : verbose
    -a                  : always regenerate working files
    --live-boost-repo   : path to the git repository storing the unmodularized boost'''

# Generate the boost file manifest from the live git repo
# found at live_boost_repo_dir
def gen_manifest(live_boost_repo_dir):
    if not live_boost_repo_dir:
        print 'Error: ', boost_manifest_pkl, ' not found and --live-boost-repo not specified'
        usage()
        sys.exit(2)
    if not os.path.isdir(os.path.normpath(os.path.join(live_boost_repo_dir, '.git'))):
        print 'Error: ', live_boost_repo_dir, ' is not a valid git repository'
        usage()
        sys.exit(2)
    if verbose:
        print '[INFO] generating manifest from ', live_boost_repo_dir
    # boost = 'boost'
    boost = os.path.normpath(os.path.join('boost', 'assign'))
    libs = 'libs'
    # Read the files in the boost directory and put them in a list
    o = Popen(['git', 'ls-files', boost], \
        stdout=PIPE, cwd=live_boost_repo_dir, shell=True).communicate()[0]
    boost_manifest = o.split('\n')
    with open(boost_manifest_pkl, 'wb') as f:
        pickle.dump(boost_manifest, f)

def main():
    # Parse the command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ahv", ["help", "live-boost-repo="])
    except getopt.GetoptError, err:
        print 'Error: ', str(err)
        usage()
        sys.exit(2)
    live_boost_repo_dir = None
    regen_boost_manifest = False
    for o, a in opts:
        if o == "-v":
            global verbose
            verbose = True
        elif o == "-a":
            regen_boost_manifest = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o == "--live-boost-repo":
            live_boost_repo_dir = a
        else:
            assert False, "unhandled option"

    # Write a file containing all the files in the live boost
    # git repository if the user asked us to.
    if regen_boost_manifest:
        gen_manifest(live_boost_repo_dir)

    # Load the boost file manifest from the pickle
    try:
        # Try to read the pickle
        with open(boost_manifest_pkl, 'rb') as f:
            boost_manifest = pickle.load(f)
    except IOError:
        # pickle wasn't there, generate it:
        gen_manifest(live_boost_repo_dir)
        with open(boost_manifest_pkl, 'rb') as f:
            boost_manifest = pickle.load(f)

    if verbose:
        print '[INFO] Boost manifest:'
        print '    ' + '\n    '.join(boost_manifest)

if __name__ == "__main__":
    main()
