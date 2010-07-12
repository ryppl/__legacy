import os, sys, getopt, stat, pickle, posixpath
from subprocess import PIPE, Popen

boost_manifest_pkl = 'boost_manifest.cache'
verbose = False

# Print the usage message (there's probably a nifty python way to do this)
def usage():
    print '''Usage: findmoddiffs.py [-h] [-a] [-v] [--source=<dir>]
    -h          : help
    -v          : verbose
    -a          : always regenerate working files
    --source    : path to the git repository storing the unmodularized boost'''

# Generate the boost file manifest from the live git repo
# found at live_boost_repo_dir
def gen_manifest(live_boost_repo_dir):
    if not live_boost_repo_dir:
        print 'Error: ', boost_manifest_pkl, ' not found and --source not specified'
        usage()
        sys.exit(2)
    if not os.path.isdir(os.path.normpath(os.path.join(live_boost_repo_dir, '.git'))):
        print 'Error: ', live_boost_repo_dir, ' is not a valid git repository'
        usage()
        sys.exit(2)
    if verbose:
        print '[INFO] generating manifest from ', live_boost_repo_dir
    # Read the files in the boost directory and put them in a list
    o = Popen(['git ls-files boost'], \
        stdout=PIPE, cwd=live_boost_repo_dir, shell=True).communicate()[0]
    files = o.split('\n')
    # Read the files in the libs directory and put them in a list
    o = Popen(['git ls-files libs'], \
        stdout=PIPE, cwd=live_boost_repo_dir, shell=True).communicate()[0]
    files.extend(o.split('\n'))
    with open(boost_manifest_pkl, 'wb') as input:
        existing = [f for f in files if f != '']
        existing.sort()
        pickle.dump(existing, input, -1)

def main():
    # Parse the command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ahv", ["help", "source="])
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
        elif o == "--source":
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
        with open(boost_manifest_pkl, 'rb') as input:
            existing = pickle.load(input)
    except IOError:
        # pickle wasn't there, generate it:
        gen_manifest(live_boost_repo_dir)
        with open(boost_manifest_pkl, 'rb') as input:
            existing = pickle.load(input)
    
    if verbose:
        print '[INFO] Boost manifest:'
        print '[INFO]     ' + '\n[INFO]     '.join(existing)

    try:
        # Read the manifest containing the modularization mappings
        with open('manifest.txt', 'r') as input:
            # Parse lines like "R100 some/src/path/ some/dst/path/" into
            # a sorted list of "some/src/path/"
            #manifest = [os.path.normcase(line.split('\t')[1]) for line in input if line[:4] == 'R100']
            manifest = [line.split('\t')[1] for line in input if line[:4] == 'R100']
            manifest.sort()
    except IOError:
        print 'Error: can not find file manifest.txt'
        sys.exit(1)

    # Make "manifest" and "existing" essentially a map of paths to counts.
    # Use lists instead of dictionaries to keep ordering intact, and
    # use nested lists instead of tuples so we can modify the count
    # in-place.
    manifest = [[f,0] for f in manifest]
    existing = [[f,0] for f in existing]

    fsi = manifest.__iter__()
    exi = existing.__iter__()

    # Iterate over the manifast and the existing files in lock step
    # advancing one or the other or both as necessary and keeping
    # track in the counts which paths appear in both lists and which
    # don't.
    try:
        f = fsi.next()
        e = exi.next()
        while 1:
	    # If the paths are the same, (e.g. they're both 'foo/bar.hpp')
	    # then inc the count for each and advance both iterators
            if f[0] == e[0]:
                f[1] += 1
                e[1] += 1
                f = fsi.next()
                e = exi.next()
	    # If the path as listed in the manifest sorts after the
	    # current path in the repo, advance the repo's iterator
	    # so it catches up.
            elif f[0] > e[0]:
                e = exi.next()
	    # If the manifest path is a directory and the repo path
	    # represents a file in that directory, in the count for
	    # both, but only advance the repo iterator. There may
	    # yet me more files in this directory to count.
            elif f[0][-1] == '/' and e[0].startswith(f[0]):
                f[1] += 1
                e[1] += 1
                e = exi.next()
	    # Otherwise, the manifest path sorts before the repo path
	    # and is not a parent directory of the repo path, so advance
	    # the manifest iterator so it catches up.
            else:
                f = fsi.next()
    except StopIteration:
        pass

    # Display the files that are in the repo that are
    # not accounted for in the manifest.
    print '\nChecking existing files against manifest ...'
    for e in existing:
        if 0 == e[1]:
            print '\tmissed', e[0]
    
    # Display the files and directories in the manifest that
    # have no correspondence with files or directories in the
    # repo.
    print '\nChecking manifest against existing files ...'
    for f in manifest:
        if 0 == f[1]:
            print '\tmissed', f[0]
        
if __name__ == "__main__":
    main()
