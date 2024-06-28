__version__ = "0.1.0"

import argparse
import inspect
import os
import sys
from typing import Annotated, Callable, get_args, get_origin


def _has_default_value(param: inspect.Parameter):
    return param.default is not inspect._empty


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
                # Set default values for the arguments parameters which may be
                # overriden.
                help = None
                type_ = str
                default = None
                optional_prefix = ""
                envvar = None

                if (annot := param.annotation) is not inspect._empty:
                    type_ = annot
                    if get_origin(annot) is Annotated:
                        annot_args = get_args(annot)
                        # NOTE: Only the first instance of an `Argument` is considered
                        for arg in annot_args:
                            if isinstance(arg, Argument):
                                help = arg.help
                                envvar = arg.envvar
                                break

                if _has_default_value(param):
                    default = param.default
                    optional_prefix = "--"

                    # If we are using an envvar we use it only if it is available on
                    # the environemnt otherwise don't do anything, ie. keep the default
                    if envvar is not None:
                        try:
                            default = os.environ[envvar]
                        except KeyError:
                            pass

                else:
                    if envvar is not None:
                        e_ = (
                            "Envvars are not supported for arguments without a default."
                        )
                        raise ValueError(e_)

                cmd_parser.add_argument(
                    f"{optional_prefix}{param_name}",
                    type=type_,
                    default=default,
                    help=help,
                )

                self._registered_commands[function.__name__] = function

            return function

        return f


class Argument:
    def __init__(self, help: str | None = None, envvar: str | None = None):
        self.help = help
        self.envvar = envvar
