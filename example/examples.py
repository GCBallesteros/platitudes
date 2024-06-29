from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Annotated
from uuid import UUID

import platitudes as pl

app = pl.Platitudes()


@app.command()
def cmd1(name: str, surname: str = "Holy", am_i_awesome: bool = True):
    print(f"Hello {name} {surname}")
    print(f"Awesome? {am_i_awesome}")


@app.command()
def cmd2(
    name: Annotated[str, pl.Argument(help="Author name")],
    surname: str,  # No help but still positional
    photo_file: Annotated[
        Path, pl.Argument(help="Path to the photo file", exists=True)
    ] = Path("./my_pic.jpeg"),
):
    print(f"My name {name} {surname}")
    print(f"My picture: {photo_file}")

    raise pl.Exit()  # Early exit!!
    print("Not reachable!")


@app.command()
def cmd3(is_rainy: bool = False):
    print(f"Is it rainy? {is_rainy}")


@app.command()
def cmd4(
    book_uuid: UUID, another_uuid: UUID = UUID("d48edaa6-871a-4082-a196-4daab372d4a1")
):
    print(f"Book UUID: {book_uuid}")
    print(f"Other UUID: {another_uuid}")


@app.command()
def cmd5(town: str | None = None):
    print(f"Town: {town}")


class Color(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2


@app.command()
def cmd6(color: Color = Color.RED):
    print(f"Color of party town: {color}")


@app.command()
def cmd7(birthday: datetime):
    print(f"My BDay is on: {birthday}")


if __name__ == "__main__":
    app()
