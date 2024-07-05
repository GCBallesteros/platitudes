String work just as you would expect them to. Whatever text you put into the CLI option will get passsed straight into your function.

!!! note

    If the string contains white space remember to put the whole thing in double
    quotes. For example `python cli.py --full-name "John Doe"`

## Examples

Without a default value it would look like:


```python
import platitudes as pl

def say_my_name(name: str):
    print(f"Call me {name}")

pl.run(say_my_name)

# Using this CLI: python cli.py Sophia
```

and if you otherwise want a default then just provide it to the function:

```python
import platitudes as pl

def say_my_name(name: str = "Stacey"):
    print(f"Call me {name}")

pl.run(say_my_name)

# Using this CLI with the default: python cli.py
# or without it: python cli.py --say-my-name Monica
```
