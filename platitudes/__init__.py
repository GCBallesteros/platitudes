__version__ = "0.1.0"

import argparse
import inspect
import os
import sys
from pathlib import Path
from typing import Annotated, Callable, get_args, get_origin

# TODO: Refactor the command parsing a bit
# TODO: Better error message
# TODO: Type hints for the action not being helpful
# TODO: Finish Path stuff


def _has_default_value(param: inspect.Parameter):
    return param.default is not inspect._empty


class Platitudes:
    def __init__(self):
        self._registered_commands: dict[str, Callable] = {}
        self._parser = argparse.ArgumentParser()
        self._subparsers = self._parser.add_subparsers()

    def __call__(self) -> None:
        try:
            args_ = self._parser.parse_args()
        except PlatitudeError as e:
            print("\n", e, "\n")
            print(self._parser.format_help())
            sys.exit(1)

        main_command = self._registered_commands[sys.argv[1]]

        args_dict = dict(args_._get_kwargs())

        try:
            main_command(**args_dict)
        except Exit:
            sys.exit(0)

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
                action: str | argparse.Action = "store"
                extra_annotations = None

                if (annot := param.annotation) is not inspect._empty:
                    type_ = annot

                    if get_origin(annot) is Annotated:
                        annot_args = get_args(annot)
                        # Unnest the type from `Annotated` parameters
                        type_ = annot_args[0]
                        # NOTE: Only the first instance of an `Argument` is considered
                        for arg in annot_args:
                            if isinstance(arg, Argument):
                                extra_annotations = arg
                                break

                    if extra_annotations is not None:
                        help = extra_annotations.help
                        envvar = extra_annotations.envvar

                    if type_ is bool:
                        if not _has_default_value(param):
                            e_ = (
                                "Boolean parameters must always supply a default."
                                f"This wasn't provided for {param}"
                            )
                            raise ValueError(e_)
                        action = argparse.BooleanOptionalAction
                    elif type_ is Path:
                        action = extra_annotations._path_action

                if _has_default_value(param):
                    default = param.default
                    optional_prefix = "--"

                    # Use the envvar if it is available
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
                    f"{optional_prefix}{param_name.replace('_', '-')}",
                    type=type_,
                    default=default,
                    help=help,
                    action=action,
                )

                self._registered_commands[function.__name__] = function

            return function

        return f


class Argument:
    def __init__(
        self,
        help: str | None = None,
        envvar: str | None = None,
        # Path
        exists: bool = False,
        file_okay: bool = True,
        dir_okay: bool = True,
        writable: bool = False,
        readable: bool = True,
        resolve_path: bool = False,
    ):
        self.help = help
        self.envvar = envvar

        # Only relevant if we are dealing with Paths
        self._path_action = make_path_action(
            exists,
            file_okay,
            dir_okay,
            writable,
            readable,
            resolve_path,
        )


class Exit(Exception):
    pass


class PlatitudeError(Exception):
    def __str__(self):
        return f"Error: {self.args[0]}"


def make_path_action(
    exists: bool = False,
    file_okay: bool = True,
    dir_okay: bool = True,
    writable: bool = False,
    readable: bool = True,
    resolve_path: bool = False,
):
    class _PathAction(argparse.Action):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __call__(self, _parser, namespace, path, _option_string=None) -> None:
            if exists and not path.exists():
                e_ = f"Invalid value for '--config': Path {path} does not exist."
                raise PlatitudeError(e_)

            if file_okay and not path.isfile():
                e_ = f"Invalid value for '--config': File {path} is a directory."
                raise PlatitudeError(e_)

            setattr(namespace, self.dest, path)

    return _PathAction
