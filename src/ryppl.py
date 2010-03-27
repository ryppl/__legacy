from optparse import OptionParser
import sys


# take a single command arg[1]
# then parse sys.argv[2:] to optionparser
# it must be space separated, commit correction to workflows doc


def install(parser=None, parameters=None):
    print ("install")
    print (parameters)
    parser.add_option("--test", action="callback", callback=call_test, callback_args=(parameters,))
    parser.parse_args(parameters)

def checkout(parameters):
    pass

def help(parser=None, parameters=None):
    print( HELP_MSG % {"program_name":sys.argv[0]})

def publish(parser=None, parameters=None):
    pass

def merge_request(parser=None, parameters=None):
    pass

def release(parser=None, parameters=None):
    pass

def show(parser=None, parameters=None):
    pass

def test(parser=None, parameters=None):
    print ("test")
    print (parameters)

def remote_test(parser=None, parameters=None):
    pass

def call_test(option, opt_str, value, parser, *args, **kwargs):
    test(parameters=args[0])



HELP_MSG = """
Usage python %(program_name)s command-name [ options... ] [ project-names... ]
where command-name is one of the following
    install
    checkout
    publish
    merge-request
    show
    test
    remote-test
options are specified with the usual syntax (--...)
and project-names are an (optional) list of space separated names.
"""
def main():
    parser = OptionParser()

    handle = {
        "help": help,
        "install": install,
        "checkout": checkout,
        "publish": publish,
        "merge-request": merge_request,
        "release": release,
        "show": show,
        "test": test,
        "remote-test": remote_test,
    }
    
    try:
        handle[sys.argv[1]](parser, sys.argv[2:])
    except KeyError:
        print HELP_MSG

if __name__ == '__main__':
    main()

