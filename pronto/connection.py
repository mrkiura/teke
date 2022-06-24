from enum import Enum
from functools import cached_property
from http.cookies import SimpleCookie
from multiprocessing.sharedctypes import Value
from typing import Any, Awaitable, Callable, Optional, Union
from urllib.parse import parse_qsl, unquote_plus

from werkzeug.datastructures import Headers, MultiDict

CoroutineFunction = Callable[[Any], Awaitable]


class ConnectionType(Enum):
    HTTP = "HTTP"
    WebSocket = "WebSocket"


class Connection:
    def __init__(
        self, scope: dict, *, send: CoroutineFunction, receive: CoroutineFunction
    ) -> None:
        pass

    @cached_property
    def request_headers(self) -> Headers:
        pass

    @cached_property
    def request_cookies(self) -> SimpleCookie:
        pass

    @cached_property
    def type(self) -> ConnectionType:
        pass

    @cached_property
    def method(self) -> str:
        pass

    @cached_property
    def path(self) -> str:
        pass

    @cached_property
    def query(self) -> MultiDict:
        pass

    async def send(self, data: Union[bytes, str]=b"", finish: Optional[bool]=False):
        pass

    async def _http_send(self, data: bytes = b"", *, finish: bool = False):
        pass

    async def finish(self, close_code: Optional[int] = 1000):
        pass

    async def start_response(self):
        pass

    async def body_iter(self):
        pass

    async def body(self) -> bytes:
        pass

    def insert_response_header(self, key, value) -> None:
        pass

    def insert_response_cookie(self, key, value) -> None:
        pass
