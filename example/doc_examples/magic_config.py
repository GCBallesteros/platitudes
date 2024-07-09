import platitudes as pl

app = pl.Platitudes()


@app.command(config_file="config-file")
def lab_runner(
    n_points: int | None = None,
    integration_time: float | None = None,
):
    print(n_points)
    print(integration_time)


app()
