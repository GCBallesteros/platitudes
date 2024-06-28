__version__ = "0.0.0"

import argparse
import inspect
import sys
from typing import Callable


class Platitudes:
    def __init__(self):
        self._registered_commands: dict[str, Callable] = {}
        self._parser = argparse.ArgumentParser()
        self._subparsers = self._parser.add_subparsers()

    def __call__(self) -> None:
        args_ = self._parser.parse_args()
        main_command = self._registered_commands[sys.argv[1]]

        args_dict = dict(args_._get_kwargs())
        main_command(**args_dict)

    def command(self):
        def f(function: Callable) -> Callable:
            cmd_parser = self._subparsers.add_parser(function.__name__)
            cmd_signature = inspect.signature(function)

            for param_name, param in cmd_signature.parameters.items():
                if (annot := param.annotation) is inspect._empty:
                    type_ = str
                else:
                    type_ = annot

                cmd_parser.add_argument(param_name, type=type_)

                self._registered_commands[function.__name__] = function

            return function

        return f
