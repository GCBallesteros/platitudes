## Using a config file to supply default values

A common pattern that I find really useful to version control the parameters
passed to complex CLI programs is to save the actual parameters on a file. My
calls to the CLI then reduce to just providing a config file, however, I still
retain the ability to manually override some of the parameters specified on the
config file. Platitudes can automatically inject an optional parameter for you
that takes as input a Path to a json config file. The values defined on this
json will then be used as defaults for the CLI parameters. Before getting into
the nitty gritty details here is an example of it at work:

```python
import platitudes as pl

app = pl.Platitudes()


@app.command(config_file="config-file")
def lab_runner(
    n_points: int,
    integration_time: float,
    camera_name: str = "RGB",
):
    print(n_points)
    print(integration_time)
    print(camera_name)


app()
```

!!! note "`pl.run` also supports config file defaults"

    This functionality is also supported by `pl.run`. That would look like:
    ```python
    def lab_runner(
        n_points: Annot[
            int,  Argument(help="How many points are being measured")
        ],
        integration_time: Annot[
            float, Argument(help="Integration time in s")
        ],
    ): ...

    pl.run(lab_runner, config_file="config-file")
    ```

The only difference with respect to all the other uses of Platitudes that have
been shown so far is the presence of the `config_file` parameter. The string
passed will be the name used for the extra injected optional argument used
to pass the configuration file. 

First we can confirm that indeed there is a new argument by printing the help
for the CLI.

```
❯ python example/doc_examples/magic_config_01.py lab_runner --help
usage: magic_config_01.py lab_runner [-h] [--n-points N_POINTS]
                                     [--integration-time INTEGRATION_TIME]
                                     [--camera-name CAMERA_NAME] --config-file CONFIG_FILE

options:
  -h, --help            show this help message and exit
  --n-points N_POINTS
  --integration-time INTEGRATION_TIME
  --camera-name CAMERA_NAME
                        - (default: RGB)
  --config-file CONFIG_FILE  <----- NEW!
```

Before really testing if it works lets create a config file for it:

```json
{
  "n_points": 3,
  "integration_time": 2.1
}
```

Two things to note here:

1. The names used in the json are the actual argument names on the function;
2. We didn't need to specify `camera_name` since it already had a default.

Let's running it again a couple of times:

```
❯ python magic_config_01.py lab_runner --config-file magic_config_01.json
N points: 3
Integration time 2.1
Camera Name: RGB
```

or we can override any of the parameters on the command line:

```
❯ python magic_config_01.py lab_runner --config-file magic_config_01.json --n-points 10 --camera-name Infrared
N points: 10
Integration time 2.1
Camera Name: Infrared
```

The astute reader might have noticed that we passed `n-points` and
`camera-name` as optional parameters, that is prefixed by `--` and in arbitrary
order despite the function signature implying they should act as positional
since they don't have a default.

!!! note "All parameters become optional when using config file defaults"

    The use of a configuration file to provide defaults turns all
    the parameters of the resulting CLI optional. This is a natural
    consequence of them having defaults provide it, even if it is
    not through the normal mechanism.


## Defaults precedence

Considering this functionality we have all in all 4 ways to set the value of a
variable when using configuration files. They are as follows ordered from highest
to lowest precedence.

1. Values provided on the command line (max precedence)
2. Defaults provided through an environment variable using
   `pl.Argument(envvar=...)`
3. Values given as a normal default in function signature
4. Values provided via the configuration file (min precedence)

You may want to have a look at `test_magic_config_priority` under
`test/test_cmdline.py` to understand the different precedences.

!!! note

    It is not ideal that normal defaults take precedence over those on the config
    file. It is therefore probably wise to avoid using _normal_ defaults in combination
    with the functionality described here.

    Unfortunately, after parsing there is no way to tell if a value obtained
    via argument parsing came from a default or from a user supplied value.

