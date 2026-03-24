import asyncio
import io
import logging
import os
import shutil
import socket
from contextlib import asynccontextmanager
from uuid import uuid4

import qrcode
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from fastsend.models import Payload

logger = logging.getLogger("uvicorn.error")
memory = {"lock": False}

# Configure the FastAPI app
templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)


def remove_file(path: str):
    try:
        os.remove(path)
    except Exception as e:
        logger.error(f"Error removing file: {e}")


def run_server(payload: Payload):
    # Default values
    id = uuid4().hex
    path = f"/{id}"

    # Check the payload
    if not payload.randomize:
        path = "/"
    if payload.path:
        path = f"/{payload.path.lstrip('/')}"

    # Create the fastapi app
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Print the URL to access the data
        ip_addr = payload.host
        if payload.host == "0.0.0.0":
            ip_addr = socket.gethostbyname(socket.gethostname())
        url = f"http://{ip_addr}:{payload.port}{path}"

        # Check the QR code option
        logger.info(f"Share link: {url}")
        if payload.qr:
            qr = qrcode.QRCode()
            qr.add_data(url)
            f = io.StringIO()
            qr.print_ascii(out=f)
            f.seek(0)
            logger.info(f"QR code:\n{f.read()}")
        yield

    app = FastAPI(lifespan=lifespan)

    # Check the data type
    _type, data = payload.get_type()
    match _type:
        case "file":
            # Define the route
            @app.get(path)
            async def get_file(
                request: Request,
            ):
                # Check the lock
                if not payload.destroy or not memory["lock"]:
                    memory["lock"] = True
                    return FileResponse(data)
                raise HTTPException(status_code=404, detail="Data not found")
        case "directory":
            archive_name = os.path.join("/tmp", id)
            name = shutil.make_archive(archive_name, "zip", data)

            # Define the route
            @app.get(path)
            async def get_directory(
                request: Request, background_tasks: BackgroundTasks
            ):
                # Add the cleanup task
                background_tasks.add_task(remove_file, name)

                # Check the lock
                if not payload.destroy or not memory["lock"]:
                    memory["lock"] = True
                    return FileResponse(name, media_type="application/zip")
                raise HTTPException(status_code=404, detail="Data not found")
        case "text":
            # Define the route
            @app.get(path, response_class=HTMLResponse)
            async def get_text(
                request: Request,
            ):
                # Check the lock
                if not payload.destroy or not memory["lock"]:
                    memory["lock"] = True
                    return templates.TemplateResponse(
                        request=request, name="text.html", context={"text": data}
                    )
                raise HTTPException(status_code=404, detail="Data not found")

    config = uvicorn.Config(app, host=payload.host, port=payload.port, log_level="info")
    server = uvicorn.Server(config)

    async def _run():
        await server.serve()

    # Run the server in a separate thread
    asyncio.run(_run())
