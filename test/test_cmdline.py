from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Annotated
from uuid import UUID

import pytest

import platitudes as pl


def test_unannotated():
    """Untyped inputs should just be treated as strings."""
    app = pl.Platitudes()

    @app.command
    def _(name):
        assert isinstance(name, str)
        assert name == "GBallesteros"

    app(["prog", "_", "GBallesteros"])


def test_str():
    """ "Check positional strings"""
    app = pl.Platitudes()

    @app.command
    def _(name: str):
        assert isinstance(name, str)
        assert name == "GBallesteros"

    app(["prog", "_", "GBallesteros"])


def test_int():
    """ "Check positional strings"""
    app = pl.Platitudes()

    @app.command
    def _(age: int):
        assert isinstance(age, int)
        assert age == 14

    app(["prog", "_", "14"])


def test_int_with_default():
    """ "Check positional strings"""
    app = pl.Platitudes()

    @app.command
    def _(age: int = 14):
        assert isinstance(age, int)
        assert age == 14

    app(["prog", "_"])


def test_bool():
    """Check optional boolean."""
    app = pl.Platitudes()

    @app.command
    def _(is_rainy: bool = False):
        assert isinstance(is_rainy, bool)
        assert is_rainy

    app(["prog", "_", "--is-rainy"])

    with pytest.raises(ValueError):

        @app.command
        def __(is_rainy: bool):
            assert isinstance(is_rainy, bool)
            assert not is_rainy

        app(["prog", "__"])


def test_uuid():
    app = pl.Platitudes()

    @app.command
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

    @app.command
    def _(color: Color = Color.RED):
        assert Color.GREEN is color

    app(["prog", "_", "--color", "1"])

    # TEST: Should fail when input is not a valid member of the enum
    with pytest.raises(SystemExit) as wrapped_error:
        app(["prog", "_", "--color", "4"])

        assert wrapped_error.type == SystemExit
        assert wrapped_error.value.code == 2


def test_datetime():
    """Check datetimes"""
    app = pl.Platitudes()

    @app.command
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
    @app.command
    def __(birthday: Annotated[datetime, pl.Argument(formats=["%Y-%m"])]):
        assert birthday == datetime(1956, 1, 1)

    app(["prog", "__", "1956-01"])

    @app.command
    def ___(
        birthday: Annotated[datetime, pl.Argument(formats=["%Y-%m"])] = datetime(
            1956, 1, 1
        ),
    ):
        assert birthday == datetime(1956, 1, 1)

    app(["prog", "___"])


def test_path_that_exists():
    app = pl.Platitudes()

    @app.command
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

    @app.command
    def _(photo_file: Annotated[Path, pl.Argument(exists=True)]):
        assert isinstance(photo_file, Path)

    with pytest.raises(SystemExit):
        app(["prog", "_", "LICENSE_"])
