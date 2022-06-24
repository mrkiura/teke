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
        pass

    def __await__(self):
        pass


class JsonResponse(HttpResponse):
    def __init__(
        self, data: Any, connection: Optional[Connection] = None, *args, **kwargs
    ):
        pass
