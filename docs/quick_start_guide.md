# Quick Start Guide

```python
from enum import Enum
from pathlib import Path
from typing import Annotated

import platitudes as pl

app = pl.Platitudes()

class Color(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2

@app.command()
def build_profile(
    name: Annotated[str, pl.Argument(help="User name")],  # Adding help strings
    surname: str,
    age: int,
    photo_file: Annotated[
        Path, pl.Argument(exists=True)  # Paths can be checked for existence
    ],
    favorite_color: Color = Color.RED,  # Optional enum argument with a default
):
    print(f"The user is named {name} {surname} and his favorite color is {favorite_color}")
    print(f"Age: {age}")
    print(f"Picture stored at: {photo_file}")

    assert isinstance(photo_file, Path)
    assert isinstance(favorite_color, Color)

if __name__ == "__main__":
    app()
```
