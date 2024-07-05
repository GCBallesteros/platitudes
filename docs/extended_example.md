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

app = pl.Platitudes(description="Manage users")


class Color(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2


@app.command()
def build_profile(
    name: Annotated[str, pl.Argument(help="User name")],
    age: int,
    photo_file: Annotated[
        Path, pl.Argument(exists=True)
    ],
    favorite_color: Color = Color.RED,
):
    print(f"User's is named {name} and they love {favorite_color}")
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
# Optionally pass a description
app = pl.Platitudes(description="Manage users")

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
    age: int,
    photo_file: Annotated[Path, pl.Argument(exists=True)],
    favorite_color: Color = Color.RED,
): ...
```

Looking at it we see that only the last argument, `favorite_color` has a
default value so we will end up with 3 postional arguments and an optional one
for it.

From the top we have the following arguments:

- __`name`__: A string that  has been `Annotated` with a `pl.Argument`. This is the mechanism
used in Platitudes to provide additional information about arguments. In this
case we are just providing a string that will be shown when the CLI help is
presented.
- __`age`__: A bare `int` without any bells and whistle.
- __`photo_file`__: An annotated `pathlib.Path` in this case the annotations is
asking Platitudes to verify that the passed file exists and otherwise raise an
error and terminate execution.

Since these first 3 arguments have no default values they will be read from the
CLI based exclusively on their position. Note that they will be received by the
underlying function as the type implied by the type hint.

The final argument is an optional one, as implied by the presence of a default
argument. When calling the CLI we can leave it out or pass it a value by
preceding it with it's name and two dashes, `--`. That is `--favorite-color 1`.

!!! note  "Optional arguments always use kebap-case"

    Underscore, `_` are turned into `-` when creating the options so they are always in
    kebap case.

would not be `1` but the an actual Enum value. This is equivalent to the
Interestingly this last argument is an Enum of ints. And the received value
`choice` parameter in
[argparse](https://docs.python.org/dev/library/argparse.html). We could have
also used an Enum of strings in which case instead of a number we would have
passed in one of the enumerated strings.

We also added another command to the CLI, `delete_profile`. This command
demonstrates the use of the
[UUID](https://docs.python.org/dev/library/uuid.html) functionality. If the
passed parameter is not a valid UUID parsing will fail and an exception will be
raised. In addittion to this, and like with all other parameters, the passed
value to the function will be an actual UUID from the standard library.

## Running it!

To run the CLI just call the program from a terminal. Lets start by showing the help
strings for the app as well as for the commands.

```
❯ python extended_example.py 
usage: extended_example.py [-h] {build_profile,delete_profile} ...

Manage users

positional arguments:
  {build_profile,delete_profile}

options:
  -h, --help            show this help message and exit


❯ python extended_example.py build_profile --help
usage: extended_example.py build_profile [-h] [--favorite-color {0,1,2}] name age photo-file

Build a user's profile.

positional arguments:
  name                  User name
  age
  photo-file

options:
  -h, --help            show this help message and exit
  --favorite-color {0,1,2}
                        - (default: Color.RED)

❯ python extended_example.py delete_profile --help
usage: extended_example.py delete_profile [-h] user

Delete a user's profile

positional arguments:
  user

options:
  -h, --help  show this help message and exit
```

See how the docstrings were used in the help itself! Finally, time to create a
new profiles:

```
❯ python extended_example.py build_profile GB 42 pic.jpeg 42                

 error: Invalid value for 'photo-file': Path pic.jpeg does not exist. 

usage: extended_example.py build_profile [-h] [--favorite-color {0,1,2}] name age photo-file

Build a user's profile.

positional arguments:
  name                  User name
  age
  photo-file

options:
  -h, --help            show this help message and exit
  --favorite-color {0,1,2}
                        - (default: Color.RED)
```

Whoops pic file wasn't there!

```
❯ touch pic.jpeg             

❯ python example/extended_example.py build_profile GB  42 pic.jpeg              
User's is named GB and they love Color.RED
Age: 42
Picture stored at: pic.jpeg
```

Victory 🎉!  This should be enough to get you started. Next you can have a look
at the support types documentation to learn more about the capabilities of
Platitudes.

- [str](types/str.md)
- [numbers](types/numbers.md)
- [datetime](types/datetie.md)
- [Booleans](types/bool.md)
- [UUID](types/uuid.md)
- [Path](types/path.md)
- [Enum/Choices](types/enum.md)
