Standard library `pathlib.Path` are also supported and can be used as any of
the other types that have been discussed already. However, many different
checks can be performed on the received paths to validate them. In particular
you can check for the following:

- Does the pointed at object exist?
- Is it readable/writable?
- Can it be a directory?
- Can it be a file?
- Do you want to auto-resolve the path?

All of this behaviours are controlled using `Annotated` types with
`platitudes.Argument` just like it is done with [`datetime`
arguments](types/datetime.md).

Here is an example where we only accept files that exist:

```python
from pathlib import Path
from typing import Annotated

import platitudes as pl


def get_filename_length(
    file: Annotated[Path, pl.Argument(exists=True, dir_okay=False)],
):
    print(len(file.name))


pl.run(get_filename_length)
```

For more details on how to perform the other validatios discussed have a look
at the [`Argument` documentation](api/argument.md).
