import sentry_sdk
import typer

from src import read_once, read_stream
from src.config import general_config

app = typer.Typer()

if general_config.SENTRY_DSN:
    sentry_sdk.init(dsn=general_config.SENTRY_DSN)


@app.command()
def read():
    measurement = read_once()
    typer.echo(measurement)


@app.command()
def stream(persist: bool = False):
    for measurement in read_stream(persist=persist):
        typer.echo(measurement)


if __name__ == "__main__":
    app()
