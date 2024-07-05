Platitudes also accepts timestamps, by default the following formats are
accepted:

- `%Y-%m-%d`
- `%Y-%m-%dT%H:%M:%S`
- `%Y-%m-%d %H:%M:%S`


and of course they will be received `datetime.datetime` instances. Parsing of
the accepted timestamps is performed sequenatially (in the same order as shown
above) and the first one that works is used.

Here is a quick example:

```python
from datetime import datetime

import platitudes as pl


def find_day_of_week(bday: datetime):
    week_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    day_of_week = bday.weekday()
    print(week_days[day_of_week])


pl.run(find_day_of_week)
```


It is also possible to provide your own list of accepted formats by using an
`Annotated` argument with the [`platitudes.Argument`](api/argument.md) object.

Here is a traditional US date format example that falls back to Y/M/D when it
is not ambiguous to do so.

```python
from datetime import datetime
from typing import Annotated

import platitudes as pl


def find_day_of_week(
    bday: Annotated[
        datetime, pl.Argument(formats=["%m-%d-%y", "%Y-%m-%d"])
    ],
):
    week_days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    day_of_week = bday.weekday()
    print(week_days[day_of_week])


pl.run(find_day_of_week)
```

!!! note

    Formats are attempted in order. Therefore the example shown above cannot
    magically deambiguate US/Rest of the world dates and it will default to the
    former.

