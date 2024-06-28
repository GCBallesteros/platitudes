import platitudes as pl

app = pl.Platitudes()


@app.command()
def main(name: str, other, surname: str = "Holy"):
    print(f"Hello {name} {surname}")


@app.command()
def alt(name: str, other: str, surname: str = "Holy", more: str = "more"):
    print(f"Alt Hello {name} {surname}")


if __name__ == "__main__":
    app()
