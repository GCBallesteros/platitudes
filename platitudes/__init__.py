__version__ = "0.0.0"

import argparse
import inspect
import sys
from typing import Callable


class Platitudes:
    def __init__(self):
        self._registered_commands: dict[str, Callable] = {}
        self.parser = argparse.ArgumentParser()
        self.subparsers = self.parser.add_subparsers()

    def __call__(self) -> None:
        args_ = self.parser.parse_args()
        main_command = self._registered_commands[sys.argv[1]]

        args_dict = dict(args_._get_kwargs())
        main_command(**args_dict)

    def command(self):
        def f(function: Callable) -> Callable:
            command_parser = self.subparsers.add_parser(function.__name__)
            command_signature = inspect.signature(function)

            for param_name, param in command_signature.parameters.items():
                if (annot := param.annotation) is inspect._empty:
                    type_ = str
                else:
                    type_ = annot

                command_parser.add_argument(param_name, type=type_)

                self._registered_commands[function.__name__] = function

            return function

        return f
