from typing import Callable, Optional, List
from .connection import Connection


def create_app(routers: Optional[List[Callable]] = None) -> Callable:
    async def asgi_app(scope, receive, send):
        conn = Connection(scope, send=send, receive=receive)
        for router in routers:
            await router(conn)
            if conn.finished:
                return
        if conn.started:
            await conn.finish()
        else:
            conn.response_status_code = 404
            await conn.send("Not found", finish=True)
    return asgi_app
