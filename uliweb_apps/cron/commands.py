from uliweb.core.commands import Command, CommandManager, get_commands
from optparse import make_option

class CronCommand(Command):
    #change the name to real command name, such as makeapp, makeproject, etc.
    name = 'cron'
    #command line parameters definition
    option_list = (
        make_option('-t', '--lock_timeout', dest='lock_timeout', default=60, type='int',
            help='Singleton lock timeout.'),
        make_option('--debug', dest='debug', default=False, action='store_true',
            help='Output debug info.'),
    )
    #help information
    help = ''
    #args information, used to display show the command usage message
    args = ''
    #if True, it'll check the current directory should has apps directory
    check_apps_dirs = True
    #if True, it'll check args parameters should be valid apps name
    check_apps = True
    #if True, it'll skip not predefined parameters in options_list, otherwise it'll
    #complain not the right parameters of the command, it'll used in subcommands or
    #passing extra parameters to a special command
    skip_options = False
    #if inherit the base class option_list, default True is inherit
    options_inherit = True


    def handle(self, options, global_options, *args):
        from gevent import monkey
        monkey.patch_all()

        self.get_application(global_options)

        self.do(options, global_options)

    def do(self, options, global_options):
        from .daemon import call

        call((), options, global_options)


