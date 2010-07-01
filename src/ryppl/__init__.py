# The function that is called by ryppl when it starts
def main():

    # Patch pip so that it uses our special, local setup.py file.
    # Ryppl projects don't supply their own setup.py.
    import pip, pip.req, os
    pip.req.InstallRequirement.setup_py = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'canonical_setup.py')

    # Make sure our overrides for pip's commands have been loaded and
    # registered
    import ryppl.commands.install

    # Let PIP do its thing.  All other Ryppl functionality is in
    # overrides for PIP hooks
    return pip.main()

if __name__ == '__main__':
    import sys
    sys.exit(main())
