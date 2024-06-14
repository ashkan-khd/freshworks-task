from dataclasses import dataclass
from enum import Enum


@dataclass
class FileInfo:
    path: str
    filename: str


class Providers(str, Enum):
    AWS = "AWS"
