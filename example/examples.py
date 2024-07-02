from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Annotated
from uuid import UUID

import platitudes as pl

app = pl.Platitudes()


@app.command
def cmd1(name: str, surname: str = "Holy", am_i_awesome: bool = True):
    print(f"Hello {name} {surname}")
    print(f"Awesome? {am_i_awesome}")


@app.command
def cmd2(
    name: Annotated[str, pl.Argument(help="Author name")],
    surname: str,  # No help but still positional
    photo_file: Annotated[
        Path, pl.Argument(help="Path to the photo file", exists=True)
    ] = Path("./LICENSE"),
):
    print(f"My name {name} {surname}")
    print(f"My picture: {photo_file}")
    print(type(photo_file))

    raise pl.Exit()  # Early exit!!
    print("Not reachable!")


@app.command
def cmd3(unknwon_param, is_rainy: bool = False):
    print(unknwon_param)
    print(f"Is it rainy? {is_rainy}")


@app.command
def cmd4(
    book_uuid: UUID, another_uuid: UUID = UUID("d48edaa6-871a-4082-a196-4daab372d4a1")
):
    print(f"Book UUID: {book_uuid}")
    print(f"Other UUID: {another_uuid}")


@app.command
def cmd5(town: str | None = None):
    print(f"Town: {town}")


class Color(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2


@app.command
def cmd6(color: Color = Color.RED):
    print(f"Color of party town: {color}")


@app.command
def cmd7(birthday: datetime):
    print(f"My BDay is on: {birthday}")


@app.command
def cmd8(fav_number: int):
    print(f"My fav number is: {fav_number}")


@app.command
def build_profile(
    name: Annotated[str, pl.Argument(help="User name")],  # Adding help strings
    surname: str,
    age: int,
    photo_file: Annotated[
        Path, pl.Argument(exists=True)  # Paths can be checked for existence
    ],
    favorite_color: Color = Color.RED,  # Optional enum argument with a default
):
    print(
        f"The user is named {name} {surname} and his favorite color is {favorite_color}"
    )
    print(f"Age: {age}")
    print(f"Picture stored at: {photo_file}")

    assert isinstance(photo_file, Path)
    assert isinstance(favorite_color, Color)


if __name__ == "__main__":
    app()
