import sys
from commands import handle_command
import subprocess as sub
# take a single command arg[1]
# then parse sys.argv[2:] to optionparser
# it must be space separated, commit correction to workflows doc
class Git:
    def __init__(self, git_executable="git"):
        self.git_executable = git_executable

    def git(self, *args, **kwargs):
        # From Troy Straszheim git-ryppl
        verbose = False
        def yellow(a): return a
        if 'verbose' in kwargs:
            verbose = kwargs['verbose']
            del kwargs['verbose']
        if verbose: print("$ git " + yellow(' '.join(args)))
        req=None
        if 'req' in kwargs:
            req = kwargs['req']
            del kwargs['req']
        
        p = sub.Popen((self.git_executable,)  + args,
                      bufsize=0,
                      stdin=sub.PIPE,
                      stdout=sub.PIPE,
                      stderr=sub.STDOUT,
                      **kwargs)
        stdouttxt = str(p.stdout.read())
        p.stdin.close()
        rv = p.wait()
        if verbose: print(stdouttxt)
        if req:
            if rv != req:
                raise RuntimeError("Expected exit status %d, but got %d"
                                   % (req, rv))
            else:
                if verbose: print ("Ok, returned %d as expected." % rv)
        if verbose: print("Returned %d, okay I guess." % rv) 
        return stdouttxt
        

    def check_for_git(self):
        try:
            found = self.git("", req=1, verbose=False)
            return True
        except RuntimeError:
            return False

    def install_git(self):
        INSTALL_MESSAGE = """
    I couldn't find Git in your path.  You can download it from Type the path to a Git executable
    here [TODO: default: I'll install one for you]:
    """ 
        self.git_executable = raw_input(INSTALL_MESSAGE)

def main():
    if len(sys.argv) < 2:
        handle_command("help", None)
    else:
        git = Git()
        if not git.check_for_git():
            git.install_git()
        handle_command(sys.argv[1], sys.argv[2:])

if __name__ == '__main__':
    main()

