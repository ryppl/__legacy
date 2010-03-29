"""ryppl.dist

Provides the Distribution class, which represents the module distribution
being built/installed/distributed.
"""

import distutils2.dist
from distutils2.util import check_environ, strtobool
from distutils2 import log
from distutils2.errors import (DistutilsOptionError, DistutilsArgError,
                              DistutilsModuleError)

class Distribution(distutils2.dist.Distribution):
    global_options = list(distutils2.dist.Distribution.global_options)
    global_options[-1] = global_options[-1][:2] + ('ignore .ryppl/ryppl.cfg in your home directory',)

    # 'common_usage' is a short (2-3 line) string describing the common
    # usage of the setup script.
    common_usage = """\
Common commands: (see '--help-commands' for more)

  ryppl install <module>     installs the named module
  ryppl test <module>        tests the named module
"""

    def find_config_files(self):
        """Find as many configuration files as should be processed for this
        platform, and return a list of filenames in the order in which they
        should be parsed.  The filenames returned are guaranteed to exist
        (modulo nasty race conditions).

        There are three possible config files: distutils.cfg in the
        Distutils installation directory (ie. where the top-level
        Distutils __inst__.py file lives), a file in the user's home
        directory named .pydistutils.cfg on Unix and pydistutils.cfg
        on Windows/Mac; and setup.cfg in the current directory.

        The file in the user's home directory can be disabled with the
        --no-user-cfg option.
        """
        files = []
        check_environ()

        # Where to look for the system-wide Distutils config file
        sys_dir = os.path.dirname(sys.modules['ryppl'].__file__)

        # Look for the system config file
        sys_file = os.path.join(sys_dir, "ryppl.cfg")
        if os.path.isfile(sys_file):
            files.append(sys_file)

        # What to call the per-user config file
        if os.name == 'posix':
            user_filename = ".ryppl/ryppl.cfg"
        else:
            user_filename = "ryppl/ryppl.cfg"

        # And look for the user config file
        if self.want_user_cfg:
            user_file = os.path.join(os.path.expanduser('~'), user_filename)
            if os.path.isfile(user_file):
                files.append(user_file)

        # All platforms support local setup.cfg
        local_file = user_filename
        if os.path.isfile(local_file):
            files.append(local_file)

        log.debug("using config files: %s" % ', '.join(files))
        return files

    def parse_config_files(self, filenames=None):
        from ConfigParser import ConfigParser

        if filenames is None:
            filenames = self.find_config_files()

        log.debug("Distribution.parse_config_files():")

        parser = ConfigParser()
        for filename in filenames:
            log.debug("  reading %s" % filename)
            parser.read(filename)
            for section in parser.sections():
                options = parser.options(section)
                opt_dict = self.get_option_dict(section)

                for opt in options:
                    if opt != '__name__':
                        val = parser.get(section,opt)
                        opt = opt.replace('-', '_')
                        opt_dict[opt] = (filename, val)

            # Make the ConfigParser forget everything (so we retain
            # the original filenames that options come from)
            parser.__init__()

        # If there was a "global" section in the config file, use it
        # to set Distribution options.

        if 'global' in self.command_options:
            for (opt, (src, val)) in self.command_options['global'].items():
                alias = self.negative_opt.get(opt)
                try:
                    if alias:
                        setattr(self, alias, not strtobool(val))
                    elif opt in ('verbose', 'dry_run'): # ugh!
                        setattr(self, opt, strtobool(val))
                    else:
                        setattr(self, opt, val)
                except ValueError, msg:
                    raise DistutilsOptionError, msg

    # -- Command-line parsing methods ----------------------------------

    def parse_command_line(self):
        """Parse the setup script's command line, taken from the
        'script_args' instance attribute (which defaults to 'sys.argv[1:]'
        -- see 'setup()' in core.py).  This list is first processed for
        "global options" -- options that set attributes of the Distribution
        instance.  Then, it is alternately scanned for Distutils commands
        and options for that command.  Each new command terminates the
        options for the previous command.  The allowed options for a
        command are determined by the 'user_options' attribute of the
        command class -- thus, we have to be able to load command classes
        in order to parse the command line.  Any error in that 'options'
        attribute raises DistutilsGetoptError; any error on the
        command-line raises DistutilsArgError.  If no Distutils commands
        were found on the command line, raises DistutilsArgError.  Return
        true if command-line was successfully parsed and we should carry
        on with executing commands; false if no errors but we shouldn't
        execute commands (currently, this only happens if user asks for
        help).
        """
        #
        # We now have enough information to show the Macintosh dialog
        # that allows the user to interactively specify the "command line".
        #
        toplevel_options = self._get_toplevel_options()

        # We have to parse the command line a bit at a time -- global
        # options, then the first command, then its options, and so on --
        # because each command will be handled by a different class, and
        # the options that are valid for a particular class aren't known
        # until we have loaded the command class, which doesn't happen
        # until we know what the command is.

        self.commands = []
        parser = FancyGetopt(toplevel_options + self.display_options)
        parser.set_negative_aliases(self.negative_opt)
        parser.set_aliases({'licence': 'license'})
        args = parser.getopt(args=self.script_args, object=self)
        option_order = parser.get_option_order()
        log.set_verbosity(self.verbose)

        # for display options we return immediately
        if self.handle_display_options(option_order):
            return
        while args:
            args = self._parse_command_opts(parser, args)
            if args is None:            # user asked for help (and got it)
                return

        # Handle the cases of --help as a "global" option, ie.
        # "setup.py --help" and "setup.py --help command ...".  For the
        # former, we show global options (--verbose, --dry-run, etc.)
        # and display-only options (--name, --version, etc.); for the
        # latter, we omit the display-only options and show help for
        # each command listed on the command line.
        if self.help:
            self._show_help(parser,
                            display_options=len(self.commands) == 0,
                            commands=self.commands)
            return

        # Oops, no commands found -- an end-user error
        if not self.commands:
            raise DistutilsArgError, "no commands supplied"

        # All is well: return true
        return 1

    def _get_toplevel_options(self):
        """Return the non-display options recognized at the top level.

        This includes options that are recognized *only* at the top
        level as well as options recognized for commands.
        """
        return self.global_options + [
            ("command-packages=", None,
             "list of packages that provide distutils commands"),
            ]

    def print_commands(self):
        """Print out a help message listing all available commands with a
        description of each.  The list is divided into "standard commands"
        (listed in ryppl.command.__all__) and "extra commands"
        (mentioned in self.cmdclass, but not a standard command).  The
        descriptions come from the command class attribute
        'description'.
        """
        import ryppl.command
        std_commands = ryppl.command.__all__
        is_std = {}
        for cmd in std_commands:
            is_std[cmd] = 1

        extra_commands = []
        for cmd in self.cmdclass.keys():
            if not is_std.get(cmd):
                extra_commands.append(cmd)

        max_length = 0
        for cmd in (std_commands + extra_commands):
            if len(cmd) > max_length:
                max_length = len(cmd)

        self.print_command_list(std_commands,
                                "Standard commands",
                                max_length)
        if extra_commands:
            print
            self.print_command_list(extra_commands,
                                    "Extra commands",
                                    max_length)

    def get_command_list(self):
        """Get a list of (command, description) tuples.
        The list is divided into "standard commands" (listed in
        ryppl.command.__all__) and "extra commands" (mentioned in
        self.cmdclass, but not a standard command).  The descriptions come
        from the command class attribute 'description'.
        """
        # Currently this is only used on Mac OS, for the Mac-only GUI
        # Distutils interface (by Jack Jansen)

        import ryppl.command
        std_commands = ryppl.command.__all__
        is_std = {}
        for cmd in std_commands:
            is_std[cmd] = 1

        extra_commands = []
        for cmd in self.cmdclass.keys():
            if not is_std.get(cmd):
                extra_commands.append(cmd)

        rv = []
        for cmd in (std_commands + extra_commands):
            klass = self.cmdclass.get(cmd)
            if not klass:
                klass = self.get_command_class(cmd)
            try:
                description = klass.description
            except AttributeError:
                description = "(no description available)"
            rv.append((cmd, description))
        return rv

    # -- Command class/object methods ----------------------------------

    def get_command_packages(self):
        """Return a list of packages from which commands are loaded."""
        pkgs = self.command_packages
        if not isinstance(pkgs, list):
            if pkgs is None:
                pkgs = ''
            pkgs = [pkg.strip() for pkg in pkgs.split(',') if pkg != '']
            if "ryppl.command" not in pkgs:
                pkgs.insert(0, "ryppl.command")
            self.command_packages = pkgs
        return pkgs

    def get_command_class(self, command):
        """Return the class that implements the Distutils command named by
        'command'.  First we check the 'cmdclass' dictionary; if the
        command is mentioned there, we fetch the class object from the
        dictionary and return it.  Otherwise we load the command module
        ("distutils.command." + command) and fetch the command class from
        the module.  The loaded class is also stored in 'cmdclass'
        to speed future calls to 'get_command_class()'.

        Raises DistutilsModuleError if the expected module could not be
        found, or if that module does not define the expected class.
        """
        klass = self.cmdclass.get(command)
        if klass:
            return klass

        for pkgname in self.get_command_packages():
            module_name = "%s.%s" % (pkgname, command)
            klass_name = command

            try:
                __import__ (module_name)
                module = sys.modules[module_name]
            except ImportError:
                continue

            try:
                klass = getattr(module, klass_name)
            except AttributeError:
                raise DistutilsModuleError, \
                      "invalid command '%s' (no class '%s' in module '%s')" \
                      % (command, klass_name, module_name)

            self.cmdclass[command] = klass
            return klass

        raise DistutilsModuleError("invalid command '%s'" % command)


    def get_command_obj(self, command, create=1):
        """Return the command object for 'command'.  Normally this object
        is cached on a previous call to 'get_command_obj()'; if no command
        object for 'command' is in the cache, then we either create and
        return it (if 'create' is true) or return None.
        """
        cmd_obj = self.command_obj.get(command)
        if not cmd_obj and create:
            log.debug("Distribution.get_command_obj(): " \
                      "creating '%s' command object" % command)

            klass = self.get_command_class(command)
            cmd_obj = self.command_obj[command] = klass(self)
            self.have_run[command] = 0

            # Set any options that were supplied in config files
            # or on the command line.  (NB. support for error
            # reporting is lame here: any errors aren't reported
            # until 'finalize_options()' is called, which means
            # we won't report the source of the error.)
            options = self.command_options.get(command)
            if options:
                self._set_command_options(cmd_obj, options)

        return cmd_obj

    def _set_command_options(self, command_obj, option_dict=None):
        """Set the options for 'command_obj' from 'option_dict'.  Basically
        this means copying elements of a dictionary ('option_dict') to
        attributes of an instance ('command').

        'command_obj' must be a Command instance.  If 'option_dict' is not
        supplied, uses the standard option dictionary for this command
        (from 'self.command_options').
        """
        command_name = command_obj.get_command_name()
        if option_dict is None:
            option_dict = self.get_option_dict(command_name)

        log.debug("  setting options for '%s' command:" % command_name)

        for (option, (source, value)) in option_dict.items():
            log.debug("    %s = %s (from %s)" % (option, value,
                                                         source))
            try:
                bool_opts = map(translate_longopt, command_obj.boolean_options)
            except AttributeError:
                bool_opts = []
            try:
                neg_opt = command_obj.negative_opt
            except AttributeError:
                neg_opt = {}

            try:
                is_string = isinstance(value, str)
                if option in neg_opt and is_string:
                    setattr(command_obj, neg_opt[option], not strtobool(value))
                elif option in bool_opts and is_string:
                    setattr(command_obj, option, strtobool(value))
                elif hasattr(command_obj, option):
                    setattr(command_obj, option, value)
                else:
                    raise DistutilsOptionError, \
                          ("error in %s: command '%s' has no such option '%s'"
                           % (source, command_name, option))
            except ValueError, msg:
                raise DistutilsOptionError, msg

