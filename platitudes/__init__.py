__version__ = "0.0.0"

import sys
from typing import Any


class Platitudes:
    def __init__(self):
        self._registered_commands = {}

    def __call__(self, *args: Any, **kwds: Any) -> None:
        cmd_args = sys.argv

        command_name = cmd_args[1]

        if command_name not in self._registered_commands:
            e_ = "Command not registered"
            raise Exception(e_)
        else:
            main_command = self._registered_commands[cmd_args[1]]

        name = cmd_args[2]
        main_command(name)

    def command(self):
        def f(function):
            self._registered_commands[function.__name__] = function

            return function

        return f
