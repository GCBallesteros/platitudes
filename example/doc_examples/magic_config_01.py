import platitudes as pl

app = pl.Platitudes()


@app.command(config_file="config-file")
def lab_runner(
    n_points: int,
    integration_time: float,
    camera_name: str = "RGB",
):
    print(f"N points: {n_points}")
    print(f"Integration time {integration_time}")
    print(f"Camera Name: {camera_name}")


app()
