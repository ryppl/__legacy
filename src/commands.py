from optparse import OptionParser
import sys

def install(parser=None, parameters=None):
    print ("install command")
    print ("DEBUG install parameters: " + ','.join(parameters))
    parser.add_option("--test", action="callback", callback=call_test, callback_args=(parameters,))
    parser.parse_args(parameters)

def checkout(parser=None, parameters=None):
    print ("checkout command")

def help(parser=None, parameters=None):
    print( HELP_MSG )

def publish(parser=None, parameters=None):
    print ("publish command")

def merge_request(parser=None, parameters=None):
    print ("merge-request command")

def release(parser=None, parameters=None):
    print ("release command")

def show(parser=None, parameters=None):
    print ("show command")

def test(parser=None, parameters=None):
    print ("test command")
    print (parameters)

def remote_test(parser=None, parameters=None):
    print ("remote-test command")

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

def handle_command(command=None, parameters=None):
    """handle commands from the line interface.
    """
    parser = OptionParser()

    known_cmds = {}
    known_cmds.update(ALL_COMMANDS)
    try:
        known_cmds[command](parser, parameters)    
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

