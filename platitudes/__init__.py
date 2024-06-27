__version__ = "0.0.0"

import inspect
import sys
from typing import Any


class Platitudes:
    def __init__(self):
        self._registered_commands = {}

    def __call__(self, *args: Any, **kwds: Any) -> None:
        cmd_args = sys.argv

        command_name = cmd_args[1]
        other_args = cmd_args[2:]

        if command_name not in self._registered_commands:
            e_ = "Command not registered"
            raise Exception(e_)
        else:
            main_command = self._registered_commands[cmd_args[1]]

        command_signature = inspect.signature(main_command)
        n_arguments = len(command_signature.parameters)

        if "--help" in other_args:
            # If help is present we bypass execution and show the
            # help for the command
            display_help(main_command)
            pass
        else:
            if len(other_args) > n_arguments:
                e_ = "Too many arguments!"
                raise Exception(e_)
            main_command(*other_args)

    def command(self):
        def f(function):
            self._registered_commands[function.__name__] = function

            return function

        return f


def display_help(command):
    signature = inspect.signature(command)
    print(signature)
