Booleans are also valid types on Platitudes CLIs, however, they behave
differently to other types. Booleans __always__ are expressed and behave as
optional parameters but in contrast to _normal_ optional values it is mandatory
to pass them unless a default argument has been given to them in the function
signature. That is:

1. There name is prefixed with `--` on the CLI;
2. They can be provided at any position;
3. The don't count towards the positional arguments even if they don't have a
   default value;

In addition to the rules above Platitudes generates 2 variants optional
parameters for each boolean according to the rules of
`argparse.BooleanOptionalAction`. Here are some examples to make all of this
clearer:

## Automatic bool option generation

For each bool two variants representing True/False are generated. In the example
below these would be:
- `--is-rainy`
- `--no-is-rainy`

```python
import platitudes as pl


def _(is_rainy: bool):
    print(f"Is it rainy: {is_rainy}")


pl.run(_)
```

```
❯ python bool.py --is-rainy        
Is it rainy: True

❯ python bool.py --no-is-rainy        
Is it rainy: False

```

## Booleans without a default are mandatory

Despite looking like optional parameters (they are prefixed with `--`) if a default
is not provided they must be passed. Using the same example as above this is
what happens when no default is provided:

```
❯ python bool.py              
usage: bool.py [-h] --is-rainy | --no-is-rainy
bool.py: error: the following arguments are required: --is-rainy/--no-is-rainy
```

If a default ha
