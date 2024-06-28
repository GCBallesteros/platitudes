__version__ = "0.0.0"

import argparse
import inspect
import sys
from typing import Callable


class Platitudes:
    def __init__(self):
        self._registered_commands: dict[str, Callable] = {}

    def __call__(self) -> None:
        cmd_args = sys.argv

        command_name = cmd_args[1]

        if command_name not in self._registered_commands:
            e_ = "Command not registered"
            raise Exception(e_)
        else:
            main_command = self._registered_commands[cmd_args[1]]

        command_signature = inspect.signature(main_command)

        parser = argparse.ArgumentParser()
        for param_name, param in command_signature.parameters.items():
            if (annot := param.annotation) is inspect._empty:
                type_ = str
            else:
                type_ = annot

            parser.add_argument(param_name, type=type_)

        # NOTE: Skip the program and command names
        args_ = parser.parse_args(sys.argv[2:])
        args_dict = dict(args_._get_kwargs())
        main_command(**args_dict)

    def command(self):
        def f(function: Callable) -> Callable:
            self._registered_commands[function.__name__] = function

            return function

        return f
