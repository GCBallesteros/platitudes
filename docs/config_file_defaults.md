## Using a config file to supply default values

A common pattern that I find really useful to version control the parameters
passed to complex CLI programs is to save the actual parameters in an actual
file. My calls to the CLI then reduce to just providing a config file however I
want to retain the ability to manually override some of the parameters on the
config file. To accomplish this we need to .....

All in all we have 4 ways to set the value of a variable when using the magic
config. They are as follows ordered from highest to lowest precedence.

1. Values provided on the command line (max precedence)
2. Defaults provided through an environment variable using
   `pl.Argument(envvar=...)`
3. Values given as a normal default in function signature
4. Values provided via the configuration file (min precedence)


!!! note

    It is not ideal that normal defaults take precedence over those on the config
    file. It is therefore probably wise to avoid using _normal_ defaults in combination
    with the functionality described here.

    Unfortunately, after parsing there is no way to tell if a value obtained
    via argument parsing came from a default or from a user supplied value.



One such example could be:

```python
import json
from pathlib import Path
from typing import Annotated as Annot

from platitudes import Argument, Platitudes


app = Platitudes()

@app.command(config_file="config-file")
def lab_runner(
    n_points: Annot[
        int,  Argument(help="How many points are being measured")
    ],
    integration_time: Annot[
        float, Argument(help="Integration time in s")
    ],
):
    print(f"N Points: {n_points}")
    print(f"Integration Time: {integration_time}")

```
```json
{
  "n_points": 3,
  "integration_time": 2.1
}
```
