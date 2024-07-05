from enum import Enum
from pathlib import Path
from typing import Annotated
from uuid import UUID

import platitudes as pl

app = pl.Platitudes(description="Manage users")


class Color(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2


@app.command()
def build_profile(
    name: Annotated[str, pl.Argument(help="User name")],
    age: int,
    photo_file: Annotated[Path, pl.Argument(exists=True)],
    favorite_color: Color = Color.RED,
):
    """Build a user's profile."""
    print(f"User's is named {name} and they love {favorite_color}")
    print(f"Age: {age}")
    print(f"Picture stored at: {photo_file}")

    assert isinstance(photo_file, Path)
    assert isinstance(favorite_color, Color)


@app.command()
def delete_profile(user: UUID):
    """Delete a user's profile"""
    print(f"Deleting user with UUID: {user}")
    assert isinstance(user, UUID)


if __name__ == "__main__":
    app()
