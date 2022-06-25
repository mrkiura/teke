import functools
from typing import Callable, Iterable, Optional

from werkzeug.routing import Map, RequestRedirect, Rule
from werkzeug.exceptions import MethodNotAllowed, NotFound
from .connection import Connection
from .response import HttpResponse


class Router:
    def __init__(self) -> None:
        pass

    def route(self, rule, methods=None, name=None):
        pass

    def add_route(
        self,
        *,
        rule_string: str,
        handler: Callable,
        name: Optional[str] = None,
        methods: Optional[Iterable[str]] = None
    ):
        pass

    def get_url_binding_for_connection(self, connection: Connection):
        pass

    async def __call__(self, connection: Connection):
        pass
