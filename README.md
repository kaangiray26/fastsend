# fastsend
Send data locally, fast!

## About
fastsend is a CLI tool for quickly sending local files in your local network. It uses FastAPI for creating a simple web server and allows you to share text, files, or directories.

## Quickstart
You can use fastsend right away via:
```bash
uvx fastsend "mysecretkey"
```

## Options
- `--randomize`: Randomize the URL path for added security (Default: `true`).
- `--destroy`: Automatically destroy the server after one use (Default: `true`).
- `--host`: Specify the host to run the server on (Default: `localhost`).
- `--port`: Specify the port to run the server on (Default: `8000`).
- `--path`: Specify the path to the file or directory to send (Default: `None`).
- `--qr`: Display a QR code for easy access (Default: `false`).
