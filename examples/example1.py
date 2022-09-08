from teke import JsonResponse, Router, create_app

router = Router()

@router.route("/hello/<name>")
async def hello(connection, name):
    return JsonResponse({"hello": name})

app = create_app(routers=[router])