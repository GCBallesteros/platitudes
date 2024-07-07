import os
from typing import Annotated

import platitudes as pl

os.environ["DB_PORT"] = "1234"


def start_db(
    port: Annotated[int, pl.Argument(envvar="DB_PORT")] = 5432,
):
    print(f"DB at port: {port}")


pl.run(start_db, ["prog"])
