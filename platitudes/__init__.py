from __future__ import annotations

__version__ = "0.0.1"


import argparse
import inspect
import os
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from types import UnionType
from typing import Annotated, Any, Callable, Union, get_args, get_origin

DEFAULT_DATETIME_FORMATS = ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]


def _has_default_value(param: inspect.Parameter):
    return param.default is not inspect._empty


def _is_maybe(type_hint: Any) -> bool:
    origin = get_origin(type_hint)
    # `x | None`,  Optional[x]` and `Union[x, None]`
    if origin is UnionType or origin is Union:
        args = get_args(type_hint)
        if len(args) == 2 and type(None) in args:
            return True

    return False


def _unwrap_maybe(type_hint: Any) -> type:
    origin = get_origin(type_hint)

    if origin is UnionType or origin is Union:
        args = get_args(type_hint)
        return next(arg for arg in args if arg is not type(None))

    raise TypeError("Unhandled type_hint")


def _unwrap_annotated(annot: Any) -> tuple[Any, Argument | None]:
    type_ = annot
    extra_annotations = None
    # Unwrap Annotated parameters and keep the platitudes.Argument
    if get_origin(annot) is Annotated:
        annot_args = get_args(annot)
        # Unnest the type from `Annotated` parameters
        type_ = annot_args[0]
        # NOTE: Only the first instance of an `Argument` is considered
        for arg in annot_args:
            if isinstance(arg, Argument):
                extra_annotations = arg
                break

    return type_, extra_annotations


class Platitudes:
    def __init__(self):
        self._registered_commands: dict[str, Callable] = {}
        self._parser = argparse.ArgumentParser()
        self._subparsers = self._parser.add_subparsers()

    def __call__(self, arguments: list[str] | None = None) -> None:
        if arguments is None:
            arguments = sys.argv
        else:
            pass

        try:
            args_ = self._parser.parse_args(arguments[1:])
        except PlatitudeError as e:
            print("\n", e, "\n")
            print(self._parser.format_help())
            sys.exit(1)

        main_command = self._registered_commands[arguments[1]]

        try:
            # NOTE: argparse insists on replacing _ with - for positional arguments
            # so we need to undo it
            main_command(**{k.replace("-", "_"): v for k, v in vars(args_).items()})
        except Exit:
            sys.exit(0)

    def command(self, function: Callable) -> Callable:
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
            action: str | type[argparse.Action] = "store"
            choices = None

            if (annot := param.annotation) is not inspect._empty:
                type_, extra_annotations = _unwrap_annotated(annot)

                # Check for `None | x` parameters
                if _is_maybe(type_):
                    if not _has_default_value(param):
                        e_ = (
                            "Potentially None params must provide a default. "
                            f"Missing from {param}"
                        )
                        raise PlatitudeError(e_)
                    else:
                        type_ = _unwrap_maybe(type_)

                if extra_annotations is not None:
                    help = extra_annotations.help
                    envvar = extra_annotations.envvar

                if type_ is bool:
                    if not _has_default_value(param):
                        e_ = (
                            "Boolean parameters must always supply a default."
                            "This wasn't provided for {param}"
                        )
                        raise ValueError(e_)
                    action = argparse.BooleanOptionalAction
                elif type_ is Path and extra_annotations is not None:
                    action = extra_annotations._path_action
                elif issubclass(type_, Enum):
                    choices = [e.value for e in type_]
                    action = make_enum_action(type_)
                    try:
                        # TODO: Check type is homogenous
                        type_ = type(choices[0])
                    except IndexError:
                        PlatitudeError("Enum must have at least one choice")
                elif type_ is datetime:
                    if extra_annotations is not None:
                        action = extra_annotations._datetime_action
                    else:
                        action = make_datetime_action(DEFAULT_DATETIME_FORMATS)
                    type_ = str

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
                    e_ = "Envvars are not supported for arguments without a default."
                    raise ValueError(e_)

            cmd_parser.add_argument(
                f"{optional_prefix}{param_name.replace('_', '-')}",
                type=type_,
                default=default,
                help=help,
                action=action,
                choices=choices,
            )

            self._registered_commands[function.__name__] = function

        return function


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
        # DateTime
        formats: list[str] | None = None,
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

        # Only relevant if we are dealing with Paths
        if formats is None:
            formats = DEFAULT_DATETIME_FORMATS
        self._datetime_action = make_datetime_action(formats)


class Exit(Exception):
    pass


class PlatitudeError(Exception):
    def __str__(self):
        return f"Error: {self.args[0]}"


# = = = = = = = = =  #
#  argparse Actions  #
# = = = = = = = = =  #
def make_datetime_action(formats: list[str]):
    class _DatetimeAction(argparse.Action):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __call__(
            self, _parser, namespace, datetime_value, _option_string=None
        ) -> None:
            def parse_datetime(datetime_: str) -> datetime:
                for possible_format in formats:
                    try:
                        parsed_datetime = datetime.strptime(datetime_, possible_format)
                        return parsed_datetime
                    except ValueError:
                        pass

                raise PlatitudeError("Could not parse datetime.")

            setattr(namespace, self.dest, parse_datetime(datetime_value))

    return _DatetimeAction


def make_enum_action(enum_):
    class _EnumAction(argparse.Action):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __call__(self, _parser, namespace, enum_value, _option_string=None) -> None:
            def find_enum_field(value):
                for member in enum_:
                    if member.value == value:
                        return member

            setattr(namespace, self.dest, find_enum_field(enum_value))

    return _EnumAction


def make_path_action(
    exists: bool = False,
    file_okay: bool = True,
    dir_okay: bool = True,
    writable: bool = False,
    readable: bool = True,
    resolve_path: bool = False,
) -> type[argparse.Action]:
    class _PathAction(argparse.Action):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __call__(self, _parser, namespace, path, _option_string=None) -> None:
            resolved_path = path.resolve()

            if resolve_path:
                path = path.resolve()

            if exists and not resolved_path.exists():
                e_ = f"Invalid value for '{self.dest}': Path {path} does not exist."
                raise PlatitudeError(e_)

            if file_okay and not resolved_path.is_dir():
                e_ = f"Invalid value for '{self.dest}': File {path} is a directory."
                raise PlatitudeError(e_)

            if dir_okay and resolved_path.is_file():
                e_ = f"Invalid value for '--config': File {path} is a file."
                raise PlatitudeError(e_)

            if readable and not os.access(path, os.R_OK):
                e_ = f"Invalid value for '{self.dest}': Path {path} is not readable."
                raise PlatitudeError(e_)

            if writable and not os.access(path, os.W_OK):
                e_ = f"Invalid value for '{self.dest}': Path {path} is not writable."
                raise PlatitudeError(e_)

            setattr(namespace, self.dest, path)

    return _PathAction
