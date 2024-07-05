# Platitudes
<h4 align="center">
  <a href="https://platitudes.maxwellrules.com">Documentation</a>
</h4>

A zero dependency clone of Typer. The most convenient way to make CLI out of your programs.

## Installation

Platitudes is available on [pypi](https://pypi.org/project/platitudes/):

```
pip install platitudes
```

if you really want to avoid pulling code from the internet you can just vendor
it into your project by copying the `platitudes` folder into it. As long as you
are running Python>=3.10 everything should be fine.

## Quick Start

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

You can then show the help for `build_profile`:

```
❯ python example/readme_example.py build_profile --help
usage: readme_example.py build_profile [-h] [--favorite-color {0,1,2}] name surname age photo-file

positional arguments:
  name                  User name
  surname
  age
  photo-file

options:
  -h, --help            show this help message and exit
  --favorite-color {0,1,2}
                        - (default: Color.RED)
```

And you can run the CLI with the positional and perhaps optional arguments:

```
❯ python example/examples.py build_profile G Ballesteros 42 ./LICENSE
The user is named G Ballesteros and his favorite color is Color.RED
Age: 3
Picture stored at: LICENSE
```
