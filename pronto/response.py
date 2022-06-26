import json
from multiprocessing import connection
from typing import Union, Optional, Mapping, Any

from .connection import Connection


class HttpResponse:
    def __init__(
        self,
        body: Optional[Union[bytes, str]] = b"",
        connection: Optional[Connection] = None,
        *,
        status_code: int = 200,
        headers: Optional[Mapping[str, str]] = None
    ) -> None:
        self.body = body
        self.connection = connection
        self.status_code = status_code
        self.headers = headers

    def __await__(self):
        if not self.connection:
            raise ValueError("No connection")
        self.connection.response_status_code = self.status_code
        if self.headers:
            for key, value in self.headers.items():
                self.connection.insert_response_header(key, value)
        return self.connection.send(self.body, finish=True).__await__()
