import os, sys, getopt, pickle, ConfigParser, shutil, time, subprocess, string

# This are global constants. Do not change.
existing_cache_pkl = 'existing.cache'
is_win32 = (sys.platform == 'win32')

# These are controlled by command-line parameters
args = []
verbose = False
debug = False
src_repo_dir = None
dst_repo_dir = None
dst_module_dir = None
regen_existing_cache = False
start_at = None
stop_at = None
sections = None

# Print the usage message (there's probably a nifty python way to do this)
def usage():
    print '''Usage: findmoddiffs.py [-h] [-a] [-v] [--src=<dir>] [--dst=<dir>] [--start-at=<dir>] [--stop-at=<dir>]
    -h              : help
    -v              : verbose
    -a              : always regenerate the cache of existing boost files
    --src           : local path to the git repository storing the unmodularized boost
    --dst           : local path to the git repository storing the modularized boost
    --start-at      : section in the manifest at which to start the copy
    --stop-at       : section in the manifest at which to stop the copy
    --sections      : comma-separated list of section in the manifest to copy'''

def run(*args, **kwargs):
    if verbose: print "[INFO] ", string.join(args, ' ')
    return subprocess.check_call(args,
                                 cwd=kwargs['cwd'] if 'cwd' in kwargs else dst_module_dir,
                                 shell=is_win32)

def popen(*args, **kwargs):
    if verbose: print "[INFO] ", string.join(args, ' ')
    return subprocess.Popen(args, stdout=subprocess.PIPE,
                            cwd=kwargs['cwd'] if 'cwd' in kwargs else dst_module_dir,
                            shell=is_win32).communicate()[0]

def parse_command_line():
    global args

    # Parse the command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ahvd", ["help", "src=", "dst=", "start-at=", "stop-at=", "sections="])
    except getopt.GetoptError, err:
        print 'Error: ', str(err)
        usage()
        sys.exit(2)

    global verbose, regen_existing_cache, src_repo_dir, dst_repo_dir
    global sections, start_at, stop_at, debug
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o == "-d":
            debug = True
        elif o == "-a":
            regen_existing_cache = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o == "--src":
            src_repo_dir = a
        elif o == "--dst":
            dst_repo_dir = a
        elif o == "--start-at":
            start_at = a
        elif o == "--stop-at":
            stop_at = a
        elif o == "--sections":
            sections = a.split(',')
        else:
            assert False, "unhandled option"

    if sections is not None:
        if start_at is not None or stop_at is not None:
            print >>sys.stderr, 'If --sections is specified, you cannot', \
                'specify --start-at or --stop-at'
            sys.exit(2)

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
    o = popen('git', 'ls-files', 'boost', cwd=src_repo_dir)
    files = o.split('\n')

    # Read the files in the libs directory and put them in a list
    o = popen('git', 'ls-files', 'libs', cwd=src_repo_dir)
    files.extend(o.split('\n'))

    # Read the files in the tools directory and put them in a list
    o = popen('git', 'ls-files', 'tools', cwd=src_repo_dir)
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

    if debug:
        print '[DEBUG] Existing boost files:'
        print '[DEBUG]     ' + '\n[DEBUG]     '.join(existing_files)
        print '[DEBUG]\n'

    # The list of files found in the manifest
    manifest_files = []

    # For every source file that has a mapping, add it to the
    # manifest_files list
    for section in manifest.sections():
        for item in manifest.items(section):
            # items beginning with '<' are special
            if not item[0][0] == '<':
                manifest_files.append(item[0])
    manifest_files.sort()

    if debug:
        print '[DEBUG] Modularized boost manifest_files:'
        print '[DEBUG]     ' + '\n[DEBUG]     '.join(manifest_files)
        print '[DEBUG]\n'

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
            print '[ERROR] No destination for existing file:', e[0]

    # Display the files and directories in the manifest_files that
    # have no correspondence with files or directories in the
    # repo.
    if verbose:
        print '[INFO] Checking manifest against existing files ...'
    for f in manifest_files:
        if 0 == f[1]:
            errors += 1
            print '[ERROR] No source found corresponding to:', f[0]

    # If we encountered any errors, bail
    if not errors == 0:
        print '[ERROR] Unaccounded for files. Please fix the manifest and re-run.'
        sys.exit(1)

def clean_dir(dst_module_dir):
    for i in range(10):
        try:
            files = [os.path.normpath(os.path.join(dst_module_dir, f))
                for f in os.listdir(dst_module_dir) if not f.startswith('.git')]
            for file in files:
                if os.path.isdir(file):
                    shutil.rmtree(file)
                else:
                    os.remove(file)
            return
        except:
            print '[WARNING] Retrying to clean directory', dst_module_dir
            time.sleep(.5)
    print '[ERROR] Cannot clean directory', dst_module_dir
    sys.exit(1)

def update_modules():
    # Parse the manifest
    manifest = ConfigParser.ConfigParser()
    manifest.optionxform = str # preserve case in key names
    manifest.read('manifest.txt')

    # validate the manifest against the live repo. We had
    # better know how to relocate /every/ file before we do anything
    # else. This will abort the program if validation fails.
    validate_manifest(manifest)

    # Sort the section names so we can iterate them in order.
    # We do this so that if anything fails mid-way, the user
    # can specify the --start-at option to pick up where the
    # script last left off.
    global sections
    if sections is not None:
        for section in sections:
            if section not in manifest.sections():
                print >>sys.stderr, '%s is not a section in manifest.txt' % section
                sys.exit(2)
    else:
        sections = [section for section in manifest.sections() if section != '<ignore>']
    sections.sort()

    # validate the command line params
    global start_at, stop_at
    if start_at is not None and start_at not in sections:
        print >>sys.stderr, '%s is not a section in manifest.txt' % start_at
        sys.exit(2)
    if stop_at is not None and stop_at not in sections:
        print >>sys.stderr, '%s is not a section in manifest.txt' % start_at
        sys.exit(2)

    # If the user has asked to restart at a given section, skip all until
    # we get to that one.
    if start_at is not None and stop_at is not None:
        sections = [section for section in sections if section >= start_at and section <= stop_at]
    elif start_at:
        sections = [section for section in sections if section >= start_at]
    elif stop_at:
        sections = [section for section in sections if section <= stop_at]

    # Iterate over the sections, which represent submodules. For each
    # submodule, make sure we're on the branch 'master', remove all the
    # files, copy all the files from their source locations into their
    # destinations, add all the files that were copied, unstage the
    # removal of files marked as <new>, apply any patches and commit.
    for section in sections:
        # Construct the directory in which this submodule lives.
        global dst_module_dir
        dst_module_dir = os.path.normpath(os.path.join(dst_repo_dir, section))
        print 'Processing module at:', dst_module_dir

        if os.path.isdir(dst_module_dir):
            # make sure we're on the master branch
            o = popen('git', 'branch')
            lines = [l for l in o.split('\n') if not l == '']
            if len(lines):
                run('git', 'checkout', 'master')
                run('git', 'rm', '--quiet', '-r', '.') # remove everything

                new_module = False
            else:
                new_module = True
        else:
            os.makedirs(dst_module_dir)
            base = os.path.basename(section)
            run('git', 'init')
            run('git', 'remote', 'add', 'origin',
                'git@github.com:boost-lib/%s.git' % base)
            run('git', 'config', 'branch.master.remote', 'origin')
            run('git', 'config', 'branch.master.merge', 'refs/heads/master')
            run('git', 'submodule', 'add', 'git://github.com/boost-lib/%s.git' % base,
                section, cwd=dst_repo_dir)
            run('git', 'commit', '-a', '-m', 'Added submodule %s' % base, cwd=dst_repo_dir)
            new_module = True

        # Make sure we've really removed everything (leaving behind the top-level)
        # .git directory
        clean_dir(dst_module_dir)

        for key, value in manifest.items(section):
            # We'll handle these special keys later
            if key[0] == '<':
                continue

            # These are files we're specifically not copying
            if value == '<ignore>':
                continue

            src_path = os.path.normpath(os.path.join(src_repo_dir, key))
            dst_path = os.path.normpath(os.path.join(dst_module_dir, value))

            if verbose:
                print '[INFO] About to copy...'
                print '[INFO]     from :', src_path
                print '[INFO]     to   :', dst_path

            # copy the files from src to target
            if key[-1] == '/':
                shutil.copytree(src_path, dst_path)
            else:
                if not os.path.isdir(os.path.dirname(dst_path)):
                    if verbose:
                        print '[INFO] Making directory:', os.path.dirname(dst_path)
                    os.makedirs(os.path.dirname(dst_path))
                shutil.copy2(src_path, dst_path)

            if verbose: print '[INFO] Copied'

            # Add the files we just copied
            run('git', 'add', value)

        # Handle the files that are new to the modularized boost
        if manifest.has_option(section, '<new>'):

            # add back the files we want to keep
            new_files = manifest.get(section, '<new>').split('\n')
            for file in new_files:
                if new_module:
                    if verbose:
                        print '[INFO] Create', file, 'in', dst_module_dir
                    path = os.path.join(dst_module_dir, file)
                    if not os.path.isdir(os.path.dirname(path)):
                        os.makedirs(os.path.dirname(path))
                    fd = open(path, "w")
                    fd.write('')
                    fd.close()
                    run('git', 'add', file)
                else:
                    if verbose:
                        print '[INFO] Adding back', file, 'in', dst_module_dir
                    run('git', 'checkout', '-f', 'HEAD', '--', file)

        # If this library has a patch file specified, apply it.
        if manifest.has_option(section, '<patch>') and not new_module:

            patch = os.path.abspath(manifest.get(section, '<patch>'))
            if verbose:
                print '[INFO] Applying patch', patch, 'in', dst_module_dir
            run('git', 'apply', patch)

            # Find out what changed as a result of the patch and add those files
            o = popen('git', 'status', '--porcelain', '--untracked-files=no')
            lines = [l for l in o.split('\n') if not l == '']
            for line in lines:
                # line matches the regex [ MARC][ MD] file( -> file2)?
                file = line[3:].split(' -> ')[0]
                if verbose:
                    print '[INFO] Adding patched file', file
                run('git', 'add', file)

        if verbose:
            print '[INFO] Committing changes to module at:', dst_module_dir

        # everything looks good, so commit locally
        o = popen('git', 'status', '--porcelain', '--untracked-files=no')
        lines = [l for l in o.split('\n') if not l == '']
        if len(lines):
            run('git', 'commit', '-m', 'latest from svn')

def push_modules():
    # We now want to 'git add' all the modified submodules to the supermodule,
    # commit them and push the new boost supermodule.
    print 'Pushing all modified submodues...'

    # Push the changes in each submodule to the remote repo
    run('git', 'submodule', 'foreach', 'git', 'push', 'origin', 'master',
        cwd=dst_repo_dir)

    # We now want to 'git add' all the modified submodules to the supermodules,
    # commit them and push the new boost supermodule.
    print 'Adding all modified submodues to the boost supermodule...'

    # Run the submodule foreach command and echo the $path to each
    o = popen('git', 'submodule', '--quiet', 'foreach', 'echo $path', cwd=dst_repo_dir)
    module_paths = [mp for mp in o.split('\n') if not mp == '']

    # For each submodule in boost, 'git add' it.
    for module_path in module_paths:
        run('git', 'add', module_path, cwd=dst_repo_dir)

    print 'Committing the boost supermodule...'
    o = popen('git', 'status', '--porcelain', '--untracked-files=no', cwd=dst_repo_dir)
    lines = [l for l in o.split('\n') if not l == '']
    if len(lines):
        run('git', 'commit', '-m' 'latest from svn', cwd=dst_repo_dir)

    # Push this change up to the origin
    print 'Pushing the boost supermodule...'
    run('git', 'push', 'origin', 'master', cwd=dst_repo_dir)

    print 'Done'

if __name__ == "__main__":
    parse_command_line()

    if "update" in args: update_modules()
    if "push" in args:   push_modules()
