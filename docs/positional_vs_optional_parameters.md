Most command line interfaces (CLI) are made of a combinations of positional and
optional parameters. The former are specified in an order dependent manner when
passing them into the CLI. The latter can be given (or not) in any order but
require the user to give their name before the actual value.

For example a program that took the following arguments:

- `positional1`
- `positional2`
- `first-optional`
- `second-optional`

Could be called in any of the following ways:

```
# <xxx> to be replaced with the actual value
cli <positional1> <positional2>  # only positional args
# or
cli <positional1> <positional2>  --first-optional <some-optional>
# or with the two optional in reversed ord
cli <positional1> <positional2>  --second-optional <second-optional> --first-optional <first-optional>
```

!!! note

    In this context optional means something different to `typing.Optional`, that is,
    a variable that maybe contains a value. These, or equivalently `x | None` are
    a bit special in a Platitudes CLI program as will be described below.


## Postional and Optional Arguments in Platitudes

Platitudes CLIs are created by registering Python functions with Platitudes
apps or calling the `platitudes.run` function on them. Each of the parameters
of the function will end up mapping to a CLI parameter. Whether they end up
positional or optional depends on the presence of a default value. Parameters
without default values map to positional arguments and those with default to
positional ones. The name for the optional parameters will always change
underscores, `_` for `-` dashes.


!!! note

    Booleans are a bit special and directly contradict the previous paragraph
    in their behaviour. See the [boolean type documentation](types/bool.md)
    for more details.

## `typing.Optional` parameters

A.K.A. `x | None` or `typing.Union[x, None]` are treated differently and are also the
ONLY valid use of _mixed_ types on a Platitudes CLI. Since there is no obvious way
to pass a `None` value as a CLI parameter, Platitudes opts to:

1. Force any parameter that can be `None` via a `Union` to be optional ,in the sense described on the previous section;
2. That the default value must be `None`.

The following would be a valid Platitudes CLI:
```python
import platitudes as pl


def my_cli(param1: int | None = None, param2: str | None=None):
    print(param1)


pl.run(my_clie)
```

While this would __NOT__ be a valid CLI:

```python
import platitudes as pl


def my_cli(param1: int | None = None, param2: str | None="some_value"):
    print(param1)


pl.run(my_clie)
```

Writing a CLI where all parameters are a union with `None` as in the examples
above enables a particularly useful idiom where we can use a configuration file
to set the actual default values or override them by specifying them on the
command line. Check out the [Funky Idioms](funky_idioms.py) sections to see how
it's done.
