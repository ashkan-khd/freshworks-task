from enum import Enum
from typing import Optional


class FileInfo:
    def __init__(self, path: Optional[str], filename: Optional[str]) -> None:
        assert bool(path) == bool(filename), "`path` and `filename` must be sent together."
        self.path = path
        self.filename = filename
    
    def __bool__(self):
        return bool(self.path)


class Providers(str, Enum):
    AWS = "AWS"
