from pronto import Connection, JsonResponse, Router, create_app
# from pronto.connection import Connection
# from pronto.response import JsonResponse
# from pronto.router import Router

router = Router()

@router.route("/hello/<name>")
async def hello(connection, name):
    return JsonResponse({"hello": name})

app = create_app(routers=[router])