"""The most convenient zero dependency CLI builder"""

from __future__ import annotations

import argparse
import inspect
import os
import sys
from collections.abc import Callable
from datetime import datetime
from enum import Enum
from pathlib import Path
from types import UnionType
from typing import Annotated, Any, Union, cast, get_args, get_origin
from uuid import UUID

from .actions import (
    FloatAction,
    IntAction,
    PlatitudesAction,
    StrAction,
    UUIDAction,
    make_enum_action,
)
from .argument import Argument
from .errors import PlatitudesError

# TODO: Internal docstrings
# TODO: Shown default valid datetime formats
# TODO: Fix fake cast


def _create_parser(
    main: Callable, cmd_parser: argparse.ArgumentParser, config_file: str | None = None
) -> tuple[argparse.ArgumentParser, dict[str, type[PlatitudesAction]]]:
    cmd_signature = inspect.signature(main)

    argument_actions: dict[str, type[PlatitudesAction]] = {}
    for param_name, param in cmd_signature.parameters.items():
        help = None  # noqa: A001
        envvar = None

        if (annot := param.annotation) is not inspect._empty:
            pass
        else:
            annot = str

        type_, extra_annotations = _unwrap_annotated(annot)
        action, choices = _handle_type_specific_behaviour(
            _handle_maybe(type_, param), extra_annotations
        )

        # In theory this can be extracted from the argument parser in practice
        # it is just much more convenient to collect them here
        argument_actions[param_name] = action

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
        add_argument_kwargs["default"] = (
            default if (not config_file or default is not None) else None
        )
        add_argument_kwargs["help"] = help
        add_argument_kwargs["action"] = action
        add_argument_kwargs["choices"] = choices

        optional_prefix = optional_prefix if not config_file else "--"
        cmd_parser.add_argument(
            f"{optional_prefix}{param_name.replace('_', '-')}", **add_argument_kwargs
        )

    if config_file is not None:
        cmd_parser.add_argument(
            f"--{config_file}", default=None, type=Path, required=True
        )

    return cmd_parser, argument_actions


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
            raise PlatitudesError(e_)
        else:
            type_ = _unwrap_maybe(type_)
    return type_


def _handle_type_specific_behaviour(
    type_, extra_annotations
) -> tuple[type[PlatitudesAction], list[Any] | None]:
    choices = None

    actions: dict[type[Any], type[PlatitudesAction]] = {
        bool: cast(type[PlatitudesAction], argparse.BooleanOptionalAction),  # not true
        Path: extra_annotations._path_action,
        datetime: extra_annotations._datetime_action,
        int: IntAction,
        float: FloatAction,
        str: StrAction,
        UUID: UUIDAction,
    }

    if issubclass(type_, Enum):
        choices = [str(e.value) for e in type_]
        action = make_enum_action(type_)
    elif type_ in actions:
        action = actions[type_]
    else:
        e_ = "Unsupported type"
        raise PlatitudesError(e_)

    return action, choices


def _get_default(
    param, envvar: str | None, action, param_name: str, type_: Any
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
        raise PlatitudesError(e_)

    if type_ is bool:
        optional_prefix = "--"

    return default, optional_prefix


def _merge_magic_config_with_argv(
    magic_config_name: str | None,
    args_: argparse.Namespace,
    argument_actions: dict[str, type[PlatitudesAction]],
) -> dict[str, Any]:
    import json

    cmdline_args = {k.replace("-", "_"): v for k, v in vars(args_).items()}

    if magic_config_name is not None:
        config_attr_name = magic_config_name.replace("-", "_")
        config_attr = getattr(args_, config_attr_name)

        if config_attr is not None:
            magic_config_path = Path(config_attr)
            with magic_config_path.open("r") as fh:
                magic_config = json.load(fh)

            for param, action in argument_actions.items():
                if param in magic_config:
                    parsed_value = action.process(magic_config[param], "")
                    magic_config[param] = parsed_value

            # Remove config as it is special. All the remaining ones
            # are required by the function
            del cmdline_args[config_attr_name]
            config = magic_config | {
                arg: val for arg, val in cmdline_args.items() if val is not None
            }

            missing_params = []
            args = [arg for arg in cmdline_args]
            for arg in args:
                if arg not in config:
                    missing_params.append(arg)

            if len(missing_params) > 0:
                e_ = (
                    "The following mandatory config params have not been"
                    f" passed: {missing_params}"
                )
                raise PlatitudesError(e_)
        else:
            config = cmdline_args
    else:
        config = cmdline_args

    return config


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
        self._command_actions: dict[str, dict[str, type[PlatitudesAction]]] = {}
        self._with_magic_config: str | None = None

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
        except PlatitudesError as e:
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

        config = _merge_magic_config_with_argv(
            self._with_magic_config, args_, self._command_actions[arguments[1]]
        )

        try:
            # NOTE: argparse insists on replacing _ with - for positional arguments
            # so we need to undo it
            main_command(**config)
        except Exit:
            sys.exit(0)

    def command(self, config_file: str | None = None) -> Callable:
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

            cmd_parser, argument_actions = _create_parser(
                function, cmd_parser, config_file
            )

            if config_file is not None:
                self._with_magic_config = config_file

            self._registered_commands[function.__name__] = function
            self._command_actions[function.__name__] = argument_actions

            return function

        return proc_command


def run(
    main: Callable, arguments: list[str] | None = None, config_file: str | None = None
) -> None:
    """Create a Platitudes CLI out of a single function.

    Platitudes provides to ways to generate CLIs: `pl.Platitudes` and `pl.run`.
    The latter, unlike a `pl.Platitudes`, doesn't allow to add subcommands to
    the CLI ala `git add/fetch/...` however it's much simpler to use as it only
    requires us to pass the function to `pl.run`.

    Parameters
    ----------
    main
        The function that will form the base for the new CLI
    arguments
        List of strings passed for the CLI parsing. Defaults to using
        `sys.argv`.
    config_file
        Name of the additional optional parameter that may be injected to
        provide default values via a json file. For more information on this
        functionality consult [Config File Defaults](config_file_defaults.md)

    Example
    -------
    ```python
    import platitudes as pl

    def hello_world(name: str = "World"):
        print(f"Hello {name}!")

    pl.run(hello_world)
    ```
    """
    cmd_parser = argparse.ArgumentParser(
        description=inspect.getdoc(main),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cmd_parser, command_actions = _create_parser(main, cmd_parser, config_file)

    if arguments is None:
        arguments = sys.argv
    else:
        pass

    args_ = cmd_parser.parse_args(arguments[1:])

    config = _merge_magic_config_with_argv(config_file, args_, command_actions)
    try:
        main(**config)
    except Exit:
        sys.exit(0)


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
