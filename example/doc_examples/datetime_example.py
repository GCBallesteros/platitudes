from datetime import datetime

import platitudes as pl


def find_day_of_week(bday: datetime):
    week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_of_week = bday.weekday()
    print(week_days[day_of_week])


pl.run(find_day_of_week)
