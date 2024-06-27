import platitudes as pl

app = pl.Platitudes()

@app.command()
def main(name: str):
    print(f"Hello {name}")

if __name__ == "__main__":
    app()
