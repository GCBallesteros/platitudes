from typing import Annotated

from platitudes import Argument, Platitudes

app = Platitudes()


@app.command(config_file="config-file")
def lab_runner(
    n_points: int | None = None,
    integration_time: float | None = None,
):
    print(n_points)
    print(integration_time)


app()
