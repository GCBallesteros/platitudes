# Platitudes

Platitudes builds CLI interfaces out of your functions based on the type hints
provided on its signature. It aims to be a zero-dependency drop in replacement
for [Typer](https://typer.tiangolo.com/). If you are familiar with Typer then
you will immediately feel at home with Platitudes.

## Features

- Zero dependency
- Easy to use
- Minimal boilerplate


## Installation

Platitudes is available on [pypi](https://pypi.org/project/platitudes/):

```
pip install platitudes
```

if you really want to avoid pulling code from the internet you can just vendor
it into your project by copying the `platitudes` folder into it. As long as you
are running Python>=3.10 everything should be fine.

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

Next move into the  [Extended Example](extended_example.md) were a more
elaborate CLI is built and explained in detail.
