"""Exceptions"""

from typing import Optional


class FileSizeException(Exception):
    """Raised when a file is too large for Discord"""

    def __init__(self, limit: int, filesize: Optional[int] = None):
        super().__init__()
        self.filesize = filesize
        self.limit = limit


class NoVideoException(Exception):
    """Raised when a Tweet doesn't have a video"""
