import platitudes as pl

app = pl.Platitudes()


@app.command()
def main(name: str, other, surname: str = "Holy"):
    print(f"Hello {name} {surname}")


if __name__ == "__main__":
    app()