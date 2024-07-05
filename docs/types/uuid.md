Platitudes also comes with support for the UUID type from the standard library. As with all
other supported types all you need to do is supply it at the command line and Platitudes will
figure out how to parse it appropriately.

```python
from uuid import UUID

import platitudes as pl


def read_uuid(some_uuid: UUID):
    print(f"Your uuid is: {some_uuid}")
    print(f"Version {some_uuid.version}")


pl.run(read_uuid)
```
