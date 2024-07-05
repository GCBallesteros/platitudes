Using `Enum`s as the type for the CLI parameters makes it possible to restrict
the accepted values to the function to finite set. To accomplish this an `Enum`
object which will hold the possible values needs to be defined first. This will match
labels to values. Here is an example:

```python
from enum import Enum

import platitudes as pl


class Fruits(Enum):
    Banana = 0
    Apple = 1
    Kiwi = 2
```

!!! note "Only homogenous Enums are valid"

    Platitudes only understand `Enum` subclasses where the values associated to each
    label are of the same type. In the example above that would be integers. Another
    common choice is using strings.

With the definition above we can create a CLI and test it:
```python
def fruit_scores(fruit: Fruits):
    match fruit:
        case Fruits.Banana:
            print("Good")
        case Fruits.Apple:
            print("Meh")
        case Fruits.Kiwi:
            print("Super delicious")
        case _:
            raise ValueError("Pyright should be screaming at you")


pl.run(fruit_scores)
```

And we can test it:
```
❯ python enum_example.py --help
usage: enum_example.py [-h] {0,1,2}

positional arguments:
  {0,1,2}

options:
  -h, --help  show this help message and exit

❯ python enum_example.py 2 
Super delicious

❯ python enum_example.py 3
usage: enum_example.py [-h] {0,1,2}
enum_example.py: error: argument fruit: invalid choice: '3' (choose from '0', '1', '2')
```

Of course `Enum` parameters can be also made optional by giving them a default
as in:
```python
def fruit_scores(fruit: Fruits = Fruits.Banana):  ...
```
