# Extended Example

Now we are going to build something a bit more fancy. We will have some
subcommands, think `git status/commit/merge...`, and showcase a few more of the
features of Platitudes. 

First the full listing

```python
from enum import Enum
from pathlib import Path
from typing import Annotated
from uuid import UUID

import platitudes as pl

app = pl.Platitudes()

class Color(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2

@app.command()
def build_profile(
    name: Annotated[str, pl.Argument(help="User name")],
    surname: str,
    age: int,
    photo_file: Annotated[
        Path, pl.Argument(exists=True)
    ],
    favorite_color: Color = Color.RED,
):
    print(f"User's is named {name} {surname} and they love {favorite_color}")
    print(f"Age: {age}")
    print(f"Picture stored at: {photo_file}")

    assert isinstance(photo_file, Path)
    assert isinstance(favorite_color, Color)


@app.command()
def delete_profile(user: UUID):
    print(f"Deleting user with UUID: {user}")
    assert isinstance(user, UUID)


if __name__ == "__main__":
    app()
```

First of and differently of the example on the [intro](index.md) we instantiate a `Platitudes`
object onto which we will register the different subcommands and finally run the CLI
by just calling it. To register new subcommands all that needs to be done is to apply
the `command` decorator to them:

```python
app = pl.Platitudes()

@app.command()
def build_profile(...): ...

@app.command()
def delete_profile(...): ...

if __name__ == "__main__":
    app()
```

Then we will be able to access the subcommands as:

```
❯ python cli.py build_profile --help
❯ python cli.py delete_profile --help
```

!!! note

    The `app.command` decorator doesn't change the decorated function in any
    way meaning that outside of the context of the CLI you can use it just as well
    as you did before. This is also why we hide the call to `app()` under the if.

Now lets inspect the function signature for the `build_profile` command.

```python
@app.command()
def build_profile(
    name: Annotated[str, pl.Argument(help="User name")],
    surname: str,
    age: int,
    photo_file: Annotated[Path, pl.Argument(exists=True)],
    favorite_color: Color = Color.RED,
): ...
```

Looking at it we see that only the last argument, `favorite_color` has a
default value so we will end up with 4 postional arguments and an optional one
for it. From the top our first argument is the user's `name` we can see it's a
string but it has been `Annotated` with a `pl.Argument`. This is the mechanism
used in Platitudes to provide additional information about arguments. In this
case we are just providing a string that will be shown when the CLI help is
presented. Next is `surname`, this was is simpler, just a `str` without any
extra bells and whistles. Then comes `age` an `int`. Again it is unannotated
interesting, it's an annotated `pathlib.Path` so it will be passed into the
function as an actual `Path` object in addition to that the annotations is
asking Platitudes to verify that the passed file exists and otherwise raise and
error and terminate execution. All of the 4 for arguments are interpreted based
on their position as CLI arguments. Finally

!!! note  "Optional arguments always use kebap-case"

    Underscore, `_` are turned into `-` when creating the options so they are always in
    kebap case.



