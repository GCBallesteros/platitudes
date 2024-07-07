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
❯ python bool_01.py --is-rainy        
Is it rainy: True

❯ python bool_01.py --no-is-rainy        
Is it rainy: False
```

## Booleans without a default are mandatory

Despite looking like optional parameters (they are prefixed with `--`) if a default
is not provided they must be passed. Using the same example as above this is
what happens when no default is provided:

```
❯ python bool_01.py              
usage: bool.py [-h] --is-rainy | --no-is-rainy
bool.py: error: the following arguments are required: --is-rainy/--no-is-rainy
```

## Booleans with a default are not mandatory

Of course if a default is provided then we don't need to explicitly pass it.

```python
import platitudes as pl


def _(is_rainy: bool = False):
    print(f"Is it rainy: {is_rainy}")


pl.run(_)
```

```
❯ python bool_02.py
Is it rainy: False
```

But keep in mind that the `--is-rainy` variant still represents True! And the
`--no-xxx` variant represents False regardless of the default value.


```
❯ python bool_02.py  --no-is-rainy
Is it rainy: False

❯ python bool_02.py  --is-rainy
Is it rainy: True
```


## Booleans don't count towards the positional arguments

Even when no default is provided they are still optional in the sense that they
can be specified at any location and don't count towards the positional
arguments.

```python
import platitudes as pl


# is_rainy should nominally behave as positional but bools are special
def _(cloud_cover: float, is_rainy: bool, humidity: float, pressure: float = 1.0):
    print(f"The cloud cover is: {cloud_cover}%")
    print(f"Is it rainy: {is_rainy}")
    print(f"The humidity is: {humidity}%")
    print(f"The pressure is {pressure} atm")


pl.run(_)
```

And all the following work despite `is_rainy` being the second argument to the
function and not having a default value.

```
❯ python bool_03.py 10 20 --is-rainy
The cloud cover is: 10.0%
Is it rainy: True
The humidity is: 20.0%
The pressure is 1.0 atm

❯ python bool_03.py 10 20 --pressure 1.1 --is-rainy 
The cloud cover is: 10.0%
Is it rainy: True
The humidity is: 20.0%
The pressure is 1.1 atm
```
