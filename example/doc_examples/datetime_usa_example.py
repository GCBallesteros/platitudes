from datetime import datetime
from typing import Annotated

import platitudes as pl


def find_day_of_week(
    bday: Annotated[datetime, pl.Argument(formats=["%m-%d-%y", "%Y-%m-%d"])],
):
    week_days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    day_of_week = bday.weekday()
    print(week_days[day_of_week])


pl.run(find_day_of_week)
