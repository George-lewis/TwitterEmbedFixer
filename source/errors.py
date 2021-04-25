"""Exceptions"""


class FileSizeException(Exception):
    """Raised when a file is too large for Discord"""

    def __init__(self, filesize: int, limit: int):
        super().__init__()
        self.filesize = filesize
        self.limit = limit


class NoVideoException(Exception):
    """Raised when a Tweet doesn't have a video"""
