import os, sys, getopt, pickle, ConfigParser, shutil
from subprocess import PIPE, Popen, check_call

# This is a global constant. Do not change.
existing_cache_pkl = 'existing.cache'

# These are controlled by command-line parameters
verbose = False
src_repo_dir = None
dst_repo_dir = None
regen_existing_cache = False

# Print the usage message (there's probably a nifty python way to do this)
def usage():
    print '''Usage: findmoddiffs.py [-h] [-a] [-v] [--src=<dir>] [--dst=<dir>]
    -h      : help
    -v      : verbose
    -a      : always regenerate the cache of existing boost files
    --src   : local path to the git repository storing the unmodularized boost
    --dst   : local path to the git repository storing the modularized boost'''

def parse_command_line():
    # Parse the command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ahv", ["help", "src=", "dst="])
    except getopt.GetoptError, err:
        print 'Error: ', str(err)
        usage()
        sys.exit(2)

    for o, a in opts:
        if o == "-v":
            global verbose
            verbose = True
        elif o == "-a":
            global regen_existing_cache
            regen_existing_cache = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o == "--src":
            global src_repo_dir
            src_repo_dir = a
        elif o == "--dst":
            global dst_repo_dir
            dst_repo_dir = a
        else:
            assert False, "unhandled option"

# Generate the existing file cache from the live git repo
# found at src_repo_dir
def gen_existing_cache(src_repo_dir):

    if not src_repo_dir:
        print 'Error: ', existing_cache_pkl, ' not found and --src not specified'
        usage()
        sys.exit(2)

    if not os.path.isdir(os.path.normpath(os.path.join(src_repo_dir, '.git'))):
        print 'Error: ', src_repo_dir, ' is not a valid git repository'
        usage()
        sys.exit(2)

    if verbose:
        print '[INFO] generating existing file cache from ', src_repo_dir

    # Read the files in the boost directory and put them in a list
    o = Popen(['git ls-files boost'], \
        stdout=PIPE, cwd=src_repo_dir, shell=True).communicate()[0]
    files = o.split('\n')

    # Read the files in the libs directory and put them in a list
    o = Popen(['git ls-files libs'], \
        stdout=PIPE, cwd=src_repo_dir, shell=True).communicate()[0]
    files.extend(o.split('\n'))

    # Read the files in the tools directory and put them in a list
    o = Popen(['git ls-files tools'], \
        stdout=PIPE, cwd=src_repo_dir, shell=True).communicate()[0]
    files.extend(o.split('\n'))

    with open(existing_cache_pkl, 'wb') as input:
        existing = [f for f in files if f != '']
        existing.sort()
        pickle.dump(existing, input, -1)

# Check the manifest against the live boost mirror to ensure that we
# know where everything goes. Try reading the list of existing boost
# files from a cache so we don't have to enumerate it. Generate the
# cache if necessary.
def validate_manifest(manifest):
    # Write a file containing all the files in the live boost
    # git repository if the user asked us to.
    if regen_existing_cache:
        gen_existing_cache(src_repo_dir)

    # Load the existing_files file cache from the pickle
    try:
        # Try to read the pickle
        with open(existing_cache_pkl, 'rb') as existing_cache:
            existing_files = pickle.load(existing_cache)
    except IOError:
        # pickle wasn't there, generate it:
        gen_existing_cache(src_repo_dir)
        with open(existing_cache_pkl, 'rb') as existing_cache:
            existing_files = pickle.load(existing_cache)

    if verbose:
        print '[INFO] Existing boost files:'
        print '[INFO]     ' + '\n[INFO]     '.join(existing_files)
        print '[INFO]\n'

    # The list of files found in the manifest
    manifest_files = []

    # For every source file that has a mapping, add it to the
    # manifest_files list
    for section in manifest.sections():
        for item in manifest.items(section):
            if not item[0] == '<new>':
                manifest_files.append(item[0])
    manifest_files.sort()

    if verbose:
        print '[INFO] Modularized boost manifest_files:'
        print '[INFO]     ' + '\n[INFO]     '.join(manifest_files)
        print '[INFO]\n'

    # Make "manifest_files" and "existing_files" essentially a map of paths to counts.
    # Use lists instead of dictionaries to keep ordering intact, and
    # use nested lists instead of tuples so we can modify the count
    # in-place.
    manifest_files = [[f,0] for f in manifest_files]
    existing_files = [[f,0] for f in existing_files]

    mfi = manifest_files.__iter__()
    exi = existing_files.__iter__()

    # Iterate over the manifast and the existing_files files in lock step
    # advancing one or the other or both as necessary and keeping
    # track in the counts which paths appear in both lists and which
    # don't.
    try:
        f = mfi.next()
        e = exi.next()
        while 1:
            # If the paths are the same, (e.g. they're both 'foo/bar.hpp')
            # then inc the count for each and advance both iterators
            if f[0] == e[0]:
                f[1] += 1
                e[1] += 1
                f = mfi.next()
                e = exi.next()
            # If the path as listed in the manifest_files sorts after the
            # current path in the repo, advance the repo's iterator
            # so it catches up.
            elif f[0] > e[0]:
                e = exi.next()
            # If the manifest_files path is a directory and the repo path
            # represents a file in that directory, inc the count for
            # both, but only advance the repo iterator. There may
            # yet be more files in this directory to count.
            elif f[0][-1] == '/' and e[0].startswith(f[0]):
                f[1] += 1
                e[1] += 1
                e = exi.next()
            # Otherwise, the manifest_files path sorts before the repo path
            # and is not a parent directory of the repo path, so advance
            # the manifest_files iterator so it catches up.
            else:
                f = mfi.next()
    except StopIteration:
        pass

    # keep track of the number of errors encountered so far
    errors = 0

    # Display the files that are in the repo that are
    # not accounted for in the manifest_files.
    if verbose:
        print '[INFO] Checking existing files against manifest ...'
    for e in existing_files:
        if 0 == e[1]:
            errors += 1
            print '[INFO] No destination for existing file:', e[0]

    # Display the files and directories in the manifest_files that
    # have no correspondence with files or directories in the
    # repo.
    if verbose:
        print '[INFO] Checking manifest against existing files ...'
    for f in manifest_files:
        if 0 == f[1]:
            errors += 1
            print '[INFO] No source found corresponding to:', f[0]

    # If we encountered any errors, bail
    if not errors == 0:
        print '[ERROR] Unaccounded for files. Please fix the manifest and re-run.'
        sys.exit(1)

def main():
    # Parse the command line arguments
    parse_command_line()

    # Parse the manifest
    manifest = ConfigParser.ConfigParser()
    manifest.optionxform = str # preserve case in key names
    manifest.read('manifest.txt')

    # validate the manifest against the live repo. We had
    # better know how to relocate /every/ file before we do anything
    # else. This will abort the program if validation fails.
    validate_manifest(manifest)

    go = False

    # Iterate over the sections, which represent submodules. For each
    # submodule, check it out onto branch 'eric-boost', remove all the
    # files, copy all the files from their source locations into their
    # destinations, add all the files that were copied, unstage the
    # removal of files marked as <new>, commit and push.
    for section in manifest.sections():

        # Skip the <ignore> section
        if section == '<ignore>':
            continue

        # Construct the directory in which this submodule lives.
        dst_module_dir = os.path.normpath(os.path.join(dst_repo_dir, section))
        print 'Processing module at:', dst_module_dir

        # make sure we're on the eric-boost branch
        check_call(['git checkout -b eric-boost'], cwd=dst_module_dir, shell=True)

        # remove everything
        check_call(['git rm -r .'], cwd=dst_module_dir, shell=True)

        if not go:
            go = ('go' == raw_input('Type "go" to continue, <return> to step : '))

        for key, value in manifest.items(section):
            # We'll handle this guy later
            if key == '<new>':
                continue

            src_path = os.path.normpath(os.path.join(src_repo_dir, key))
            dst_path = os.path.normpath(os.path.join(dst_module_dir, value))

            print 'About to copy...'
            print '\tfrom :', src_path
            print '\tto   :', dst_path
            if not go:
                go = ('go' == raw_input('Type "go" to continue, <return> to step : '))

            # copy the files from src to target
            if key[-1] == '/':
                shutil.copytree(src_path, dst_path)
            else:
                print 'Making directory:', os.path.dirname(dst_path)
                if not os.path.isdir(os.path.dirname(dst_path)):
                    os.makedirs(os.path.dirname(dst_path))
                shutil.copy2(src_path, dst_path)

            print 'Copied'
            if not go:
                go = ('go' == raw_input('Type "go" to continue, <return> to step : '))

            # Add the files we just copied
            check_call(['git add ' + value], cwd=dst_module_dir, shell=True)

        # Handle the files that are new to the modularized boost
        if not manifest.has_option(section, '<new>'):
            continue

        # add back the files we want to keep
        new_files = manifest.get(section, '<new>').split('\n')
        for file in new_files:
            print 'Adding back ', file, 'in ', dst_module_dir
            check_call(['git reset HEAD ' + file], cwd=dst_module_dir, shell=True)
            check_call(['git checkout -- ' + file], cwd=dst_module_dir, shell=True)

        print 'Committing changes to module at:', dst_module_dir
        if not go:
            go = ('go' == raw_input('Type "go" to continue, <return> to step : '))

        # everything looks good, so commit locally
        check_call(['git commit -m"latest"'], cwd=dst_module_dir, shell=True)

        # Push this change up to the origin
        check_call(['git push origin eric-boost'], cwd=dst_module_dir, shell=True)

if __name__ == "__main__":
    main()
