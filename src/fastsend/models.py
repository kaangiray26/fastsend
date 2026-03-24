from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class Payload(BaseModel):
    data: str
    randomize: bool = Field(default=True)
    destroy: bool = Field(default=True)
    host: str = Field(default="localhost")
    port: int = Field(default=8000)
    path: str | None = Field(default=None)
    qr: bool = Field(default=False)

    def get_type(self) -> tuple[Literal["text", "file", "directory"], str | Path]:
        path = Path(self.data)
        if path.exists():
            if path.is_file():
                return "file", path
            elif path.is_dir():
                return "directory", path
            else:
                raise ValueError("Invalid path")
        return "text", self.data
