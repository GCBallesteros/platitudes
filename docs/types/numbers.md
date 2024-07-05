Numbers work in the same unsurprising way as [strings](types/str.md) with the
difference that they are parsed into the correct type.

## Int

Integers can be passed in any string format accepted by `int` and will raise an
error in case that fails, for example, `42.0` won't be accepted.

```python
import platitudes as pl


def age_guesser(age: int):
    if age == 42:
        print("You guessed right!")
    else:
        print("Try again!")


pl.run(age_guesser)
```



## Float

Same applies to float, but in this case the parsing is performed by `float`  so
all of `42`, `42.0` and `42e0` would be acceptable.

```python
import platitudes as pl


def calculate_vat(price: float):
    taxed_price = price * 1.2
    print(f"The new price is {taxed_price}")


pl.run(age_guesser)
```


Of course both integers and float may take a default value turning them into
optional parameters.
