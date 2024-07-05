from pathlib import Path
from typing import Annotated

import platitudes as pl


def get_filename_length(
    file: Annotated[Path, pl.Argument(exists=True, dir_okay=False)],
):
    print(len(file.name))


pl.run(get_filename_length)
