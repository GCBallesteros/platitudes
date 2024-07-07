"""The most convenient zero dependency CLI builder"""

from __future__ import annotations

__version__ = "1.1.3"


import argparse
import inspect
import os
import sys
from collections.abc import Callable
from datetime import datetime
from enum import Enum
from pathlib import Path
from types import UnionType
from typing import Annotated, Any, Union, get_args, get_origin
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
        help = None  # noqa: A001
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
        default, optional_prefix = _get_default(
            param, envvar, action, param_name, type_
        )

        add_argument_kwargs = {}
        if optional_prefix == "--":
            if type_ is bool:
                if default is not None:
                    add_argument_kwargs["required"] = False
                else:
                    add_argument_kwargs["required"] = True
            else:
                add_argument_kwargs["required"] = False

        help = (  # noqa: A001
            "-"
            if ((default is not None) and (extra_annotations.help is None))
            else extra_annotations.help
        )

        # NOTE: We pass the arguments in a dict so that we don't need separate
        # calls for positional and optional parameters
        add_argument_kwargs["type"] = str
        add_argument_kwargs["default"] = default
        add_argument_kwargs["help"] = help
        add_argument_kwargs["action"] = action
        add_argument_kwargs["choices"] = choices

        cmd_parser.add_argument(
            f"{optional_prefix}{param_name.replace('_', '-')}", **add_argument_kwargs
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

    e_ = "Unhandled type_hint"
    raise TypeError(e_)


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


def _get_default(
    param, envvar: str | None, action, param_name: str, type: Any
) -> tuple[Any, str]:
    optional_prefix = ""
    default = None
    if _has_default_value(param):
        if param.default is None:
            pass
        elif isinstance(param.default, bool):
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
    elif envvar is not None:
        e_ = "Envvars are not supported for arguments without a default."
        raise ValueError(e_)

    if type is bool:
        optional_prefix = "--"

    return default, optional_prefix


class Platitudes:
    """The easiest way to create CLI applications.

    `Platitudes` instances collect several CLI commands under a single application.
    They can then be accessed by calling them using the original function name.

    """

    def __init__(self, description: str | None = None):
        """
        Parameters
        ----------
        description
            The description that will be shown when we run the help for the whole
            application.
        """
        self._registered_commands: dict[str, Callable] = {}
        self._parser = argparse.ArgumentParser(description=description)
        self._subparsers = self._parser.add_subparsers()

    def __call__(self, arguments: list[str] | None = None) -> None:
        """Runs the CLI program.

        By default we run with the arguments passed to the CLI, that is,
        `sys.argv`, and this is what you want 99% of the time. You can however
        pass all the commands as a list of strings, this is the mechanims used
        internally for testing the code.

        Parameters
        ---------
        arguments
            List of strings passed for the CLI parsing. Defaults to using `sys.argv`.

        """
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

        if len(arguments) >= 2:
            main_command = self._registered_commands[arguments[1]]
        else:
            print(self._parser.format_help())
            sys.exit(1)

        try:
            # NOTE: argparse insists on replacing _ with - for positional arguments
            # so we need to undo it
            main_command(**{k.replace("-", "_"): v for k, v in vars(args_).items()})
        except Exit:
            sys.exit(0)

    def command(self) -> Callable:
        """Add a function to the app.

        The function will be accessible from the CLI using the original's
        function name. It is most often used as a decorator. The decorated
        function is not modified in any way and therefore can be used normally
        within your program. This is useful when we want to build CLI out of
        code that we would like to reuse for building a library.

        Example
        -------
        ```python
        import platitudes as pl

        app = pl.Platitudes(description="Say hello and goodbye")

        @app.command()
        def hello(name: str):
            print(f"Hello {name}")


        @app.command()
        def goodbye(name: str):
            print(f"Goodbye {name}")
        ```
        """

        def proc_command(function: Callable) -> Callable:
            cmd_parser = self._subparsers.add_parser(
                function.__name__,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                description=inspect.getdoc(function),
            )
            cmd_parser = _create_parser(function, cmd_parser)

            self._registered_commands[function.__name__] = function

            return function

        return proc_command


def run(main: Callable, arguments: list[str] | None = None) -> None:
    """Create a CLI program out of a single function."""
    cmd_parser = argparse.ArgumentParser(
        description=inspect.getdoc(main),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
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
    """`Argument` provides extended parsing and validation options."""

    def __init__(
        self,
        help: str | None = None,  # noqa: A002
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


        `Argument` is always added inside an Annotated type and provides the following
        functionality:

        - Adding help lines to the output of the `--help` option.
        - Reading parameters from environment variables.
        - Adding validation options for parsed
          [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#basic-use)
        - Modifying the accepted
          [datetime.datetime](https://docs.python.org/3/library/datetime.html#datetime-objects)
          for the CLI.

        Parameters
        ----------
        help: str
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
    """Raise to early quit a Platitude CLI program without erroring out.

    There are occasions in which one might want to quit middway the execution in
    a clean way. This is accomplished by raising the `platitudes.Exit` exception.
    This will be automatically catched by an internal `try/except` block and exit
    with code 0 (success).

    Example
    -------
    ```python
    import platitudes as pl

    def early_exit(processing_level: str):
        match processing_level:
            case "simple":
                print("I can do simple!")
            case _:
                print("Too much for me")
                raise pl.Exit()

    pl.run(early_exit)
    ```

    """

    pass
