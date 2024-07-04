from __future__ import annotations

__version__ = "1.0.0"


import argparse
import inspect
import os
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from types import UnionType
from typing import Annotated, Any, Callable, Union, get_args, get_origin
from uuid import UUID

from .actions import (
    _FloatAction,
    _IntAction,
    _StrAction,
    _UUIDAction,
    make_datetime_action,
    make_enum_action,
    make_path_action,
)
from .errors import PlatitudeError

DEFAULT_DATETIME_FORMATS = ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]

# TODO: Better and more docs
# TODO: Shown default valid datetime formats


def _create_parser(
    main: Callable, cmd_parser: argparse.ArgumentParser
) -> argparse.ArgumentParser:
    cmd_signature = inspect.signature(main)

    for param_name, param in cmd_signature.parameters.items():
        help = None
        envvar = None

        if (annot := param.annotation) is not inspect._empty:
            pass
        else:
            annot = str

        type_, extra_annotations = _unwrap_annotated(annot)
        action, choices = _handle_type_specific_behaviour(
            _handle_maybe(type_, param), param, extra_annotations
        )

        envvar = extra_annotations.envvar
        default, optional_prefix = _get_default(param, envvar, action, param_name)

        help = (
            "-"
            if ((default is not None) and (extra_annotations.help is None))
            else extra_annotations.help
        )

        cmd_parser.add_argument(
            f"{optional_prefix}{param_name.replace('_', '-')}",
            type=str,
            default=default,
            help=help,
            action=action,
            choices=choices,
        )
    return cmd_parser


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


def _unwrap_annotated(annot: Any) -> tuple[Any, Argument]:
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

    if extra_annotations is None:
        extra_annotations = Argument()

    return type_, extra_annotations


def _handle_maybe(type_, param):
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
    return type_


def _handle_type_specific_behaviour(
    type_, param, extra_annotations
) -> tuple[str | type[argparse.Action], list[Any] | None]:
    action: str | type[argparse.Action] = "store"
    choices = None

    if type_ is bool:
        if not _has_default_value(param):
            e_ = (
                "Boolean parameters must always supply a default."
                "This wasn't provided for {param}"
            )
            raise ValueError(e_)
        action = argparse.BooleanOptionalAction
    elif issubclass(type_, Enum):
        choices = [str(e.value) for e in type_]
        try:
            action = make_enum_action(type_)
        except IndexError:
            PlatitudeError("Enum must have at least one choice")
    elif type_ is Path:
        action = extra_annotations._path_action
    elif type_ is datetime:
        action = extra_annotations._datetime_action
    elif type_ is int:
        action = _IntAction
    elif type_ is float:
        action = _FloatAction
    elif type_ is str:
        action = _StrAction
    elif type_ is UUID:
        action = _UUIDAction

    return action, choices


def _get_default(param, envvar: str | None, action, param_name: str) -> tuple[Any, str]:
    optional_prefix = ""
    default = None
    if _has_default_value(param):
        if isinstance(param.default, bool):
            # NOTE: bool is special because we are not using an action defined
            # by us
            default = param.default
        else:
            default = action.process(param.default, param_name.replace("_", "-"))

        optional_prefix = "--"

        # Use the envvar if it is available
        if envvar is not None:
            try:
                default = action.process(
                    os.environ[envvar], param_name.replace("_", "-")
                )
            except KeyError:
                pass
    else:
        if envvar is not None:
            e_ = "Envvars are not supported for arguments without a default."
            raise ValueError(e_)
    return default, optional_prefix


class Platitudes:
    """Collect multiple commands into a single app."""

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
            print(
                self._parser._get_positional_actions()[0]  # pyright: ignore
                .choices[arguments[1]]
                .format_help()
            )
            sys.exit(1)

        main_command = self._registered_commands[arguments[1]]

        try:
            # NOTE: argparse insists on replacing _ with - for positional arguments
            # so we need to undo it
            main_command(**{k.replace("-", "_"): v for k, v in vars(args_).items()})
        except Exit:
            sys.exit(0)

    def command(self) -> Callable:
        def proc_command(function: Callable) -> Callable:
            cmd_parser = self._subparsers.add_parser(
                function.__name__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
            )
            cmd_parser = _create_parser(function, cmd_parser)

            self._registered_commands[function.__name__] = function

            return function
        return proc_command


def run(main: Callable, arguments: list[str] | None = None) -> None:
    """Create a CLI program out of a single function."""
    cmd_parser = argparse.ArgumentParser()
    cmd_parser = _create_parser(main, cmd_parser)

    if arguments is None:
        arguments = sys.argv
    else:
        pass

    args_ = cmd_parser.parse_args(arguments[1:])
    try:
        # NOTE: argparse insists on replacing _ with - for positional arguments
        # so we need to undo it
        main(**{k.replace("-", "_"): v for k, v in vars(args_).items()})
    except Exit:
        sys.exit(0)


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
        """
        Annotation to extend the behvaviour of arguments and provide help strings.

        Any variable can be read from an environment variable using the
        `envvar` parameter and have a help string provided for it using `help`.
        In addittion to this we can also provide additional checks and
        behaviours for the following types:
        - pathlib.Path
        - datetime.datetime

        Parameters
        ----------
        help
            The help string that will be presented by the CLI help.
        envvar
            If supplied we will try to get the value of the parameter
            from the environment variable being pointed at.
        exists
            If `True` argument parsing will file if the path provided
            corresponds to a non-existent file or directory.
        file_okay
            If `False` argument parsing will file if the path provided
            corresponds to a file.
        dir_okay
            If `False` argument parsing will file if the path provided
            corresponds to a directory.
        writable
            Fail argument parsing if the path doesn't correspond to a
            writable file or directory.
        readable
            Fail argument parsing if the path doesn't correspond to a
            readable file or directory.
        resolve_path
            Whether to resolve the path supplied before passing it to the
            function.
        formats
            A list of format strings that can be used in the CLI to enter
            timestamps

        """
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
    """Raise if you want to early quit a Platitude CLI program without errorin out."""

    pass
