Environment variables can be used to provide default values for arguments.
This is controlled by using `Annotated` and `platitudes.Argument`. Here is how:

```python
import os
from typing import Annotated

import platitudes as pl

os.environ["DB_PORT"] = "1234"


def start_db(
    port: Annotated[int, pl.Argument(envvar="DB_PORT")] = 5432,
):
    print(f"DB at port: {port}")


pl.run(start_db, ["prog"])
```

Running the program above without passing CLI arguments will return `1234` as
the `DB_PORT` environment variable has been set above. If this hadn't been the
case then it would've printed `5432`. Finally we could have passed in a value
for `--port`.
