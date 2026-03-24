import typer

from fastsend.backend import run_server
from fastsend.models import Payload

app = typer.Typer()


# data can be a file path or a string
@app.command()
def main(
    data: str = typer.Argument(
        ..., help="Data to send. Can be a file path or a string."
    ),
    randomize: bool = typer.Option(True, help="Whether to randomize the route."),
    destroy: bool = typer.Option(
        True, help="Whether to destroy the data after one access."
    ),
    host: str = typer.Option("localhost", help="Host to run the server on."),
    port: int = typer.Option(8000, help="Port to run the server on."),
    path: str | None = typer.Option(None, help="Path to serve the data on."),
    qr: bool = typer.Option(False, help="Whether to display a QR code for the URL."),
) -> None:
    # Prepare the payload
    payload = Payload(
        data=data,
        randomize=randomize,
        destroy=destroy,
        host=host,
        port=port,
        path=path,
        qr=qr,
    )
    run_server(payload)


if __name__ == "__main__":
    app()
