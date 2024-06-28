from pathlib import Path
from typing import Annotated

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


if __name__ == "__main__":
    app()
