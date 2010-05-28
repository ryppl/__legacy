def main():
    import pip, pip.req, os
    import ryppl.commands.install

    # Patch pip to do our bidding!
    pip.req.InstallRequirement.setup_py = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'canonical_setup.py')

    return pip.main()

if __name__ == '__main__':
    import sys
    sys.exit(main())
