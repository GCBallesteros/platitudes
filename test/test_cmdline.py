"""End to end tests for the CLI."""

import json
import os
from datetime import datetime
from enum import Enum
from pathlib import Path, PosixPath
from tempfile import NamedTemporaryFile
from typing import Annotated
from uuid import UUID

import pytest

import platitudes as pl

os.environ["TEST_DATE"] = "1956-01-31T10:00:00"


def test_unannotated():
    """Untyped inputs should just be treated as strings."""
    app = pl.Platitudes()

    @app.command()
    def _(name):
        assert isinstance(name, str)
        assert name == "GBallesteros"

    app(["prog", "_", "GBallesteros"])


def test_str():
    """ "Check positional strings"""
    app = pl.Platitudes()

    @app.command()
    def _(name: str):
        assert isinstance(name, str)
        assert name == "GBallesteros"

    app(["prog", "_", "GBallesteros"])


def test_int():
    """ "Check positional strings"""
    app = pl.Platitudes()

    @app.command()
    def _(age: int):
        assert isinstance(age, int)
        assert age == 14

    app(["prog", "_", "14"])


def test_int_with_default():
    """ "Check positional strings"""
    app = pl.Platitudes()

    @app.command()
    def _(age: int = 14):
        assert isinstance(age, int)
        assert age == 14

    app(["prog", "_"])


def test_bool():
    """Check optional boolean."""
    app = pl.Platitudes()

    @app.command()
    def _(is_rainy: bool = False):
        assert isinstance(is_rainy, bool)
        assert is_rainy

    app(["prog", "_", "--is-rainy"])

    @app.command()
    def _(is_rainy: bool = False):
        assert isinstance(is_rainy, bool)
        assert not is_rainy

    app(["prog", "_"])

    def _(is_rainy: bool):
        assert isinstance(is_rainy, bool)
        assert is_rainy

    pl.run(_, ["prog", "--is-rainy"])

    def _(is_rainy: bool):
        assert isinstance(is_rainy, bool)
        assert not is_rainy

    pl.run(_, ["prog", "--no-is-rainy"])

    with pytest.raises(SystemExit):

        @app.command()
        def __(is_rainy: bool):
            assert isinstance(is_rainy, bool)
            assert not is_rainy

        pl.run(__, ["prog"])


def test_uuid():
    """Test UUID functionality"""
    app = pl.Platitudes()

    @app.command()
    def _(
        book_uuid: UUID,
        another_uuid: UUID = UUID("d48edaa6-871a-4082-a196-4daab372d4a1"),
    ):
        assert book_uuid == UUID("d48edaa6-871a-4082-a196-4daab372d4a1")
        assert isinstance(another_uuid, UUID)

    app(
        [
            "prog",
            "_",
            "d48edaa6-871a-4082-a196-4daab372d4a1",
            "--another-uuid",
            "d48edaa6-871a-4082-a196-4daab372d4a1",
        ]
    )


def test_enum():
    """Check positional enums"""
    app = pl.Platitudes()

    class Color(Enum):
        RED = 0
        GREEN = 1
        BLUE = 2

    @app.command()
    def _(color: Color = Color.RED):
        assert Color.GREEN is color

    app(["prog", "_", "--color", "1"])

    # TEST: Should fail when input is not a valid member of the enum
    with pytest.raises(SystemExit) as wrapped_error:
        app(["prog", "_", "--color", "4"])

        assert wrapped_error.type == SystemExit
        assert wrapped_error.value.code == 2


def test_enum2():
    """Check positional enums"""
    app = pl.Platitudes()

    class Color(Enum):
        RED = 0
        GREEN = 1
        BLUE = 2

    @app.command()
    def _(color: Color = Color.RED):
        assert Color.RED is color

    app(["prog", "_"])


def test_datetime():
    """Check datetimes"""
    app = pl.Platitudes()

    @app.command()
    def _(birthday: datetime):
        assert birthday == datetime(1956, 1, 31, 10, 0, 0)

    app(["prog", "_", "1956-01-31T10:00:00"])

    # TEST: Check an unsupported datetime format
    with pytest.raises(SystemExit) as wrapped_error:
        app(["prog", "_", "1956-01"])

        assert wrapped_error.type == SystemExit
        assert wrapped_error.value.code == 2

    # TEST: Check the previous failed example works if we provide the
    # appropriate format
    @app.command()
    def __(birthday: Annotated[datetime, pl.Argument(formats=["%Y-%m"])]):
        assert birthday == datetime(1956, 1, 1)

    app(["prog", "__", "1956-01"])

    @app.command()
    def ___(
        birthday: Annotated[datetime, pl.Argument(formats=["%Y-%m"])] = datetime(
            1956, 1, 1
        ),
    ):
        assert birthday == datetime(1956, 1, 1)

    app(["prog", "___"])


def test_datetime_envvar():
    """Check datetimes"""
    app = pl.Platitudes()

    @app.command()
    def _(
        birthday: Annotated[datetime, pl.Argument(envvar="TEST_DATE")] = datetime(
            1956, 1, 31, 10, 0, 0
        ),
    ):
        assert birthday == datetime(1956, 1, 31, 10, 0, 0)

    app(["prog", "_"])


def test_datetime_envvar_no_default():
    """Check datetimes"""
    app = pl.Platitudes()

    with pytest.raises(ValueError):

        @app.command()
        def _(birthday: Annotated[datetime, pl.Argument(envvar="TEST_DATE")]):
            assert birthday == datetime(1956, 1, 31, 10, 0, 0)

        app(["prog", "_"])


def test_path_that_exists():
    """Test path existence functionality"""
    app = pl.Platitudes()

    @app.command()
    def _(
        photo_file: Annotated[Path, pl.Argument(exists=True)] = Path(
            __file__
        ).parent.parent
        / "LICENSE",
    ):
        assert isinstance(photo_file, Path)

    app(["prog", "_"])


def test_path_that_does_not_exist():
    app = pl.Platitudes()

    @app.command()
    def _(photo_file: Annotated[Path, pl.Argument(exists=True)]):
        assert isinstance(photo_file, Path)

    with pytest.raises(SystemExit):
        app(["prog", "_", "LICENSE_"])


def test_standalone_cli():
    def _(age: int = 14):
        assert isinstance(age, int)
        assert age == 14

    pl.run(_, ["prog", "--age", "14"])


def test_default_no_annotation():
    """Default values without annotation are passed as is."""

    def _(age=14):
        print(age)
        assert isinstance(age, int)
        assert age == 14

    pl.run(_, ["prog"])


def test_nonsense_default():
    """Default values without annotation are passed as is."""

    with pytest.raises(pl.PlatitudeError):

        def _(age: int = "Wut?"):  # pyright: ignore
            print(age)
            assert isinstance(age, int)
            assert age == 14

        pl.run(_, ["prog"])


def test_forgot_the_main_command():
    """ "Check positional strings"""
    app = pl.Platitudes()

    @app.command()
    def _(name: str = "G"):
        assert isinstance(name, str)
        assert name == "G"

    with pytest.raises(SystemExit):
        app(["prog"])


def test_maybe_parameters():
    """Check we can pass None"""

    def _(n_days: int | None = None):
        assert n_days is None

    pl.run(_, ["prog"])

    def _(n_days: int | None = 3):
        assert n_days == 3

    pl.run(_, ["prog"])


def test_magic_config_app_all_in_json():
    app = pl.Platitudes()

    @app.command(config_file="config-file")
    def lab_runner(
        n_points: int | None = None,
        experiment_name: str | None = None,
    ):
        assert n_points == 3
        assert experiment_name == "qwerty"

    with NamedTemporaryFile("w") as fh:
        config = {"n_points": 3, "experiment_name": "qwerty"}
        fh.write(json.dumps(config))
        fh.seek(0)
        app(["prog", "lab_runner", "--config-file", fh.name])


def test_magic_config_app_one_missing():
    app = pl.Platitudes()

    @app.command(config_file="config-file")
    def lab_runner(
        n_points: int | None = None,
        experiment_name: str | None = None,
    ):
        assert n_points == 3
        assert experiment_name == "qwerty"

    with NamedTemporaryFile("w") as fh:
        config = {"n_points": 3}
        fh.write(json.dumps(config))
        fh.seek(0)
        app(
            [
                "prog",
                "lab_runner",
                "--config-file",
                fh.name,
                "--experiment-name",
                "qwerty",
            ]
        )


def test_magic_config_not_enough():
    app = pl.Platitudes()

    @app.command(config_file="config-file")
    def lab_runner(
        n_points: int | None = None,
        experiment_name: str | None = None,
    ):
        assert n_points == 3
        assert experiment_name == "qwerty"

    with NamedTemporaryFile("w") as fh:
        config = {"n_points": 3}
        fh.write(json.dumps(config))
        fh.seek(0)
        with pytest.raises(ValueError):
            app(["prog", "lab_runner", "--config-file", fh.name])


def test_magic_config_override():
    app = pl.Platitudes()

    @app.command(config_file="config-file")
    def lab_runner(
        n_points: int | None = None,
        experiment_name: str | None = None,
    ):
        assert n_points == 3
        assert experiment_name == "asdf"

    with NamedTemporaryFile("w") as fh:
        config = {"n_points": 3, "experiment_name": "qwerty"}
        fh.write(json.dumps(config))
        fh.seek(0)

        app(
            [
                "prog",
                "lab_runner",
                "--config-file",
                fh.name,
                "--experiment-name",
                "asdf",
            ]
        )


def test_magic_config_other_types():
    app = pl.Platitudes()

    @app.command(config_file="config-file")
    def lab_runner(
        a_int: int | None = None,
        a_str: str | None = None,
        a_path: Path | None = None,
        a_uuid: UUID | None = None,
        a_datetime: datetime | None = None,
    ):
        assert a_int == 3
        assert a_str == "qwerty"
        assert a_path == PosixPath("./test.py")
        assert a_uuid == UUID("d48edaa6-871a-4082-a196-4daab372d4a1")
        assert a_datetime == datetime(2020,2,2)

    with NamedTemporaryFile("w") as fh:
        config = {
            "a_int": 3,
            "a_str": "qwerty",
            "a_path": "./test.py",
            "a_uuid": "d48edaa6-871a-4082-a196-4daab372d4a1",
            "a_datetime": "2020-02-02",
        }
        fh.write(json.dumps(config))
        fh.seek(0)

        app(["prog", "lab_runner", "--config-file", fh.name])
