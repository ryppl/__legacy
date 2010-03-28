import sys
from commands import handle_command

# take a single command arg[1]
# then parse sys.argv[2:] to optionparser
# it must be space separated, commit correction to workflows doc

def main():
    if len(sys.argv) < 2:
        handle_command("help", None)
    else:
        handle_command(sys.argv[1], sys.argv[2:])

if __name__ == '__main__':
    main()

