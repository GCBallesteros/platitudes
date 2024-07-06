## Using a config file to supply default values

A common pattern that I find really useful to version control the parameters
passed to complex CLI programs is to save the actual parameters in an actual
file. My calls to the CLI then reduce to just providing a config file however I
want to retain the ability to manually override some of the parameters on the
config file. To accomplish this we need to make all our parameters optional and
have them take `None` as default as explained on the [Positional Vs Optional
Parameters](postional_vs_optional_parameters.md) section.

One such example could be:

```python
import inspect
import json
from pathlib import Path
from typing import Annotated as Annot

from platitudes import Argument, run


def lab_runner(
    config: Annot[Path, Argument(help="CLI Configuratoin file", exists=True)],
    n_points: Annot[
        int | None, Argument(help="How many points are being measured")
    ] = None,
    integration_time: Annot[
        float | None, Argument(help="Integration time in s")
    ] = None,
):
    with config.open("r") as fh:
        json_config = json.load(fh)

    frame = inspect.currentframe()
    
    # Get the arguments and their values
    args, _, _, values = inspect.getargvalues(frame)

    cmdline_config = {
        "n_points": n_points,
        "integration_time": integration_time,
    }
    mandatory_keys = list(cmdline_config.keys())
    cmdline_config = {k: v for k, v in cmdline_config.items() if v is not None}

    config = file_config | cmdline_config

    missing_params = []
    for mandatory_key in mandatory_keys:
        if mandatory_key not in config:
            missing_params.append(mandatory_key)

    if len(missing_params) > 0:
        e_ = f"The following mandatory config params have not been passed: {missing_params}"
        raise ValueError(e_)

```
```json
{
  "n_points": 3,
  "integration_time": 2.1
}
```
