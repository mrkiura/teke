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
        self.scope = scope
        self.asgi_send = send
        self.asgi_receive = receive

        self.started = False
        self.finished = False
        self.response_headers: Headers = Headers()
        self.response_cookies: SimpleCookie = SimpleCookie()
        self.response_status_code: Optional[int] = None

        self.http_body = b""
        self.http_has_more_body = True
        self.http_received_body_length = 0

    @cached_property
    def request_headers(self) -> Headers:
        headers = Headers()
        for (k, v) in self.scope["headers"]:
            headers.add(k.decode("ascii"), v.decode("ascii"))
        return headers

    @cached_property
    def request_cookies(self) -> SimpleCookie:
        cookie = SimpleCookie()
        cookie.load(self.request_headers.get("cookie", {}))
        return cookie

    @cached_property
    def type(self) -> ConnectionType:
        connection_type_label = self.scope.get("type")
        match connection_type_label:
            case "websocket":
                return ConnectionType.WebSocket
            case "http":
                return ConnectionType.HTTP
            case _:
                raise ValueError("Unsupported connection type")

    @cached_property
    def method(self) -> str:
        return self.scope["method"]

    @cached_property
    def path(self) -> str:
        return self.scope["path"]

    @cached_property
    def query(self) -> MultiDict:
        return MultiDict(parse_qsl(unquote_plus(self.scope["query_string"].decode())))

    async def send(self, data: Union[bytes, str]=b"", finish: Optional[bool]=False):
        if self.finished:
            raise ValueError("No message can be sent when connection is closed")
        match self.type:
            case ConnectionType.HTTP:
                match data:
                    case str(data):
                        data = data.encode()

                await self._http_send(data, finish=finish)
            case _:
                raise NotImplementedError("Web Socket connection not yet supported")

    async def _http_send(self, data: bytes = b"", *, finish: bool = False):
        if not self.started:
            if finish:
                self.insert_response_header("content-length", str(len(data)))
            await self.start_response()
        await self.asgi_send(
            {"type": "http.response.body", "body": data or b"", "more_body": True}
        )
        if finish:
            await self.finish()

    async def finish(self, close_code: Optional[int] = 1000):
        match self.type:
            case ConnectionType.HTTP:
                if self.finished:
                    raise ValueError("Connection already finished")
                if not self.started:
                    self.response_status_code = 204
                    await self.start_response()
                await self.asgi_send(
                    {"type": "http.response.body", "body": b"", "more_body": False}
                )
            case _:
                raise NotImplementedError()
        self.finished = True

    async def start_response(self):
        if self.started:
            raise ValueError("Response already started")
        if not self.response_status_code:
            self.response_status_code = 200
        headers = [
            [k.encode("ascii"), v.encode("ascii")] for k, v in self.response_headers.items()
        ]
        for value in self.response_cookies.values():
            headers.append([b"Set-Cookie", value.OutputString().encode("ascii")])
        await self.asgi_send(
            {
                "type": "http.response.start",
                "status": self.response_status_code,
                "headers": headers
            }
        )
        self.started = True

    async def body_iter(self):
        if self.type != ConnectionType.HTTP:
            raise ValueError("Connection type is not HTTP")
        if self.http_received_body_length > 0 and self.http_has_more_body:
            raise ValueError("body iter is already started and is not finished")
        if self.http_received_body_length > 0 and not self.http_has_more_body:
            yield self.http_body
        request_body_length = (
            int(self.request_headers.get("content-length", "0"))
            if not self.request_headers.get("transfer-encoding") == "chunked"
            else None
        )

        while self.http_has_more_body:
            if request_body_length and self.http_received_body_length > request_body_length:
                raise ValueError("body is longer than declared")
            message = await self.asgi_receive()
            message_type = message.get("type")
            if message.get("type") == "http.disconnect":
                raise ValueError("Disconnected")
            if message_type != "http.request":
                continue
            chunk = message.get("body", b"")
            if not isinstance(chunk, bytes):
                raise ValueError("Chunk is not bytes")
            self.http_body += chunk
            self.http_has_more_body = message.get("more body", False) or False
            self.http_received_body_length += len(chunk)
            yield chunk

    async def body(self) -> bytes:
        return b"".join([chunks async for chunks in self.body_iter()])

    def insert_response_header(self, key, value) -> None:
        self.response_headers.add(key, value)

    def insert_response_cookie(self, key, value) -> None:
        self.response_cookies[key] = value
