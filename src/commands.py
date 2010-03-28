from optparse import OptionParser
import sys

def install(git, parser=None, parameters=None):
    print ("install command")
    print ("DEBUG install parameters: " + ','.join(parameters))
    parser.add_option("--test", action="callback", callback=call_test, callback_args=(parameters,))
    parser.parse_args(parameters)

def checkout(git, parser=None, parameters=None):
    print ("checkout command")
    git.git("status", verbose=True) # placeholder

def help(git, parser=None, parameters=None):
    print( HELP_MSG )

def publish(git, parser=None, parameters=None):
    print ("publish command")
    git.git("status", verbose=True) # placeholder


def merge_request(git, parser=None, parameters=None):
    print ("merge-request command")
    git.git("status", verbose=True) # placeholder


def release(git, parser=None, parameters=None):
    print ("release command")
    git.git("status", verbose=True) # placeholder


def show(git, parser=None, parameters=None):
    print ("show command")
    git.git("status", verbose=True) # placeholder


def test(git, parser=None, parameters=None):
    print ("test command")
    print (parameters)

def remote_test(git, parser=None, parameters=None):
    print ("remote-test command")
    git.git("status", verbose=True) # placeholder


def call_test(option, opt_str, value, parser, *args, **kwargs):
    test(parameters=args[0])

ALL_COMMANDS = ( # see workflows.rst
    ("help", help),
    ("install", install),
    ("checkout", checkout),
    ("publish", publish),
    ("merge-request", merge_request),
    ("release", release),
    ("show", show),
    ("test", test),
    ("remote-test", remote_test),
)

def handle_command(git, command=None, parameters=None):
    """handle commands from the line interface.
    """
    parser = OptionParser()

    known_cmds = {}
    known_cmds.update(ALL_COMMANDS)
    try:
        known_cmds[command](git, parser, parameters)    
    except KeyError:
        help(parser, parameters)

HELP_MSG = """
Usage python %(program_name)s command-name [ options... ] [ project-names... ]
where command-name is one of the following
    %(known_cmds)s
options are specified with the usual syntax (--...)
and project-names are an (optional) list of space separated names.
""" % ({"program_name": sys.argv[0],
        "known_cmds": "\n    ".join(sorted(x[0] for x in ALL_COMMANDS))})

