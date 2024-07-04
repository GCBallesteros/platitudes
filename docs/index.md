# Platitudes

Platitudes builds CLI interfaces out of your functions based on the type hints
provided on its signature. It aims to be a zero-dependency drop in replacement
for [Typer](https://typer.tiangolo.com/). If you are familiar with Typer then
you will immediately feel at home with Platitudes.

## Features

- Zero dependency
- Easy to use
- Minimal boilerplate

## Hello world example

```python
import platitudes as pl

def hello_world(name: str = "World"):
  print(f"Hello {name}!")

pl.run(hello_world)
```

Now you have a CLI! Let's check out the help:

```
❯ python example/hello_world.py --help
usage: hello_world.py [-h] [--name NAME]

options:
  -h, --help   show this help message and exit
  --name NAME  - (default: World)
```

We just have one optional parameter which means that we should be able to run
it with extra arguments.

```
❯ python hello_world.py               
Hello World!
```

or we can provide one ourselves,

```
❯ python hello_world.py --name ⭐
Hello ⭐!
```

The key takeaway is that we can generate create CLI with zero boilerplate by
calling `pl.run` and letting it figure it out from the type hints.

For a more elaborate example check out the [Quick Start Guide](quick_start_guide.md)
