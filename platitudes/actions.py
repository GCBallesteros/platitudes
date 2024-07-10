"""Actions used to parse the input values.

Platitudes leverages the use of the action parameter in argparse parsers to
take complete control of how different values are parsed. See the
argparse documentation for more details.

https://docs.python.org/3/library/argparse.html#action-classes
"""

import argparse
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from .errors import PlatitudesError


class PlatitudesAction(argparse.Action):  # noqa: D101
    @staticmethod
    def process(val, _dest) -> Any:  # noqa: D102
        raise NotImplementedError

    def __call__(self, __parser__, namespace, val_str, option_string=None) -> None:
        """Add parameter to the namespace"""
        out = self.process(val_str, self.dest)
        setattr(namespace, self.dest, out)


def make_datetime_action(formats: list[str]):
    """Produces a class responsible for parsing datetimes."""

    class _DatetimeAction(PlatitudesAction):
        @staticmethod
        def process(val, dest):
            if isinstance(val, datetime):
                return val

            def parse_datetime(datetime_: str) -> datetime:
                for possible_format in formats:
                    try:
                        # If you want non-naive datetimes you will need to specify
                        # your own formatters.
                        parsed_datetime = datetime.strptime(datetime_, possible_format)  # noqa: DTZ007
                        return parsed_datetime
                    except ValueError:
                        pass

                e_ = (
                    f"argument {dest}: invalid datetime format supplied:"
                    f" '{val}'\n Only the following are supported: {formats}"
                )
                raise PlatitudesError(e_)

            out = parse_datetime(val)
            return out

    return _DatetimeAction


def make_enum_action(enum_):
    """Produces a class responsible for parsing enums."""

    class _EnumAction(PlatitudesAction):
        @staticmethod
        def process(val, dest):
            if isinstance(val, enum_):
                return val

            def find_enum_field(value):
                for member in enum_:
                    if str(member.value) == value:
                        return member

                PlatitudesError("Enum must have at least one choice")

            out = find_enum_field(val)
            return out

    return _EnumAction


class FloatAction(PlatitudesAction):
    """Action for parsing floats"""

    @staticmethod
    def process(val, dest):
        """Process floats"""
        try:
            out = float(val)
        except ValueError:
            e_ = f"argument {dest}: invalid float value: '{val}'"
            raise PlatitudesError(e_)
        return out


class IntAction(PlatitudesAction):
    """Action for parsing int"""

    @staticmethod
    def process(val, dest):
        """Process int"""
        try:
            out = int(val)
        except ValueError:
            e_ = f"argument {dest}: invalid int value: '{val}'"
            raise PlatitudesError(e_)
        return out


class UUIDAction(PlatitudesAction):
    """Action for parsing UUID"""
    @staticmethod
    def process(val, dest):
        """Process UUID"""
        if isinstance(val, UUID):
            return val
        try:
            out = UUID(val)
        except ValueError:
            e_ = f"argument {dest}: invalid uuid value: '{val}'"
            raise PlatitudesError(e_)
        return out


class StrAction(PlatitudesAction):
    """Action for parsing strings"""
    @staticmethod
    def process(val, dest):
        "process string"
        return val


def make_path_action(
    exists: bool = False,
    file_okay: bool = True,
    dir_okay: bool = True,
    writable: bool = False,
    readable: bool = False,
    resolve_path: bool = False,
) -> type[PlatitudesAction]:
    """Produces a class responsible for parsing paths."""

    class _PathAction(PlatitudesAction):
        @staticmethod
        def process(val, dest):
            path = Path(val)
            resolved_path = path.resolve()

            if resolve_path:
                path = path.resolve()

            if exists and not resolved_path.exists():
                e_ = f"Invalid value for '{dest}': Path {path} does not exist."
                raise PlatitudesError(e_)

            if not file_okay and resolved_path.is_file():
                e_ = f"Invalid value for '{dest}': File {path} is a file."
                raise PlatitudesError(e_)

            if not dir_okay and resolved_path.is_dir():
                e_ = f"Invalid value for '{dest}': File {path} is a directory."
                raise PlatitudesError(e_)

            if readable and not os.access(path, os.R_OK):
                e_ = f"Invalid value for '{dest}': Path {path} is not readable."
                raise PlatitudesError(e_)

            if writable and not os.access(path, os.W_OK):
                e_ = f"Invalid value for '{dest}': Path {path} is not writable."
                raise PlatitudesError(e_)
            return path

    return _PathAction
