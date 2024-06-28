from pathlib import Path
from typing import Annotated

import platitudes as pl

app = pl.Platitudes()


@app.command()
def cmd1(name: str, surname: str = "Holy"):
    print(f"Hello {name} {surname}")


@app.command()
def cmd2(
    name: Annotated[str, pl.Argument(help="Author name")],
    surname: str,  # No help but still positional
    photo_file: Annotated[Path, pl.Argument(help="Path to the photo file")] = Path(
        "./my_pic.jpeg"
    ),
):
    print(f"My name {name} {surname}")
    print(f"My picture: {photo_file}")

    raise pl.Exit()  # Early exit!!
    print("Not reachable!")


if __name__ == "__main__":
    app()
