import argparse
import os
from datetime import datetime
from pathlib import Path
from uuid import UUID

from .errors import PlatitudeError


def make_datetime_action(formats: list[str]):
    class _DatetimeAction(argparse.Action):
        @staticmethod
        def process(datetime_str, dest):
            if isinstance(datetime_str, datetime):
                return datetime_str

            def parse_datetime(datetime_: str) -> datetime:
                for possible_format in formats:
                    try:
                        parsed_datetime = datetime.strptime(datetime_, possible_format)
                        return parsed_datetime
                    except ValueError:
                        pass

                e_ = f"argument {dest}: invalid datetime format supplied: '{datetime_str}'"
                raise PlatitudeError(e_)

            out = parse_datetime(datetime_str)
            return out

        def __call__(
            self, __parser__, namespace, datetime_str, option_string=None
        ) -> None:
            out = self.process(datetime_str, self.dest)
            setattr(namespace, self.dest, out)

    return _DatetimeAction


def make_enum_action(enum_):
    class _EnumAction(argparse.Action):
        @staticmethod
        def process(enum_str, dest):
            if isinstance(enum_str, enum_):
                return enum_str

            def find_enum_field(value):
                for member in enum_:
                    if str(member.value) == value:
                        return member

            out = find_enum_field(enum_str)
            return out

        def __call__(self, __parser__, namespace, enum_str, option_string=None) -> None:
            out = self.process(enum_str, self.dest)
            setattr(namespace, self.dest, out)

    return _EnumAction


class _FloatAction(argparse.Action):
    @staticmethod
    def process(float_str, dest):
        try:
            out = float(float_str)
        except ValueError:
            e_ = f"argument {dest}: invalid float value: '{float_str}'"
            raise PlatitudeError(e_)
        return out

    def __call__(self, __parser__, namespace, float_str, option_string=None) -> None:
        out = self.process(float_str, self.dest)
        setattr(namespace, self.dest, out)


class _IntAction(argparse.Action):
    @staticmethod
    def process(int_str, dest):
        try:
            out = int(int_str)
        except ValueError:
            e_ = f"argument {dest}: invalid int value: '{int_str}'"
            raise PlatitudeError(e_)
        return out

    def __call__(self, __parser__, namespace, int_str, option_string=None) -> None:
        out = self.process(int_str, self.dest)
        setattr(namespace, self.dest, out)


class _UUIDAction(argparse.Action):
    @staticmethod
    def process(uuid_str, dest):
        if isinstance(uuid_str, UUID):
            return uuid_str
        try:
            out = UUID(uuid_str)
        except ValueError:
            e_ = f"argument {dest}: invalid uuid value: '{uuid_str}'"
            raise PlatitudeError(e_)
        return out

    def __call__(self, __parser__, namespace, uuid_str, option_string=None) -> None:
        out = self.process(uuid_str, self.dest)

        setattr(namespace, self.dest, out)


class _StrAction(argparse.Action):
    @staticmethod
    def process(str_, dest):
        return str_

    def __call__(self, __parser__, namespace, int_str, option_string=None) -> None:
        out = self.process(int_str, self.dest)
        setattr(namespace, self.dest, out)

    pass


def make_path_action(
    exists: bool = False,
    file_okay: bool = True,
    dir_okay: bool = True,
    writable: bool = False,
    readable: bool = True,
    resolve_path: bool = False,
) -> type[argparse.Action]:
    class _PathAction(argparse.Action):
        @staticmethod
        def process(path_str, dest):
            path = Path(path_str)
            resolved_path = path.resolve()

            if resolve_path:
                path = path.resolve()

            if exists and not resolved_path.exists():
                e_ = f"Invalid value for '{dest}': Path {path} does not exist."
                raise PlatitudeError(e_)

            if not file_okay and resolved_path.is_file():
                e_ = f"Invalid value for '{dest}': File {path} is a file."
                raise PlatitudeError(e_)

            if not dir_okay and resolved_path.is_dir():
                e_ = f"Invalid value for '{dest}': File {path} is a directory."
                raise PlatitudeError(e_)

            if readable and not os.access(path, os.R_OK):
                e_ = f"Invalid value for '{dest}': Path {path} is not readable."
                raise PlatitudeError(e_)

            if writable and not os.access(path, os.W_OK):
                e_ = f"Invalid value for '{dest}': Path {path} is not writable."
                raise PlatitudeError(e_)
            return path

        def __call__(self, __parser__, namespace, path_str, option_string=None) -> None:
            path = self.process(path_str, self.dest)

            setattr(namespace, self.dest, path)

    return _PathAction
