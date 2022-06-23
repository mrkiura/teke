import asyncio
from pronto import Connection, HttpResponse, JsonResponse, Router, create_app
router = Router()

@router.route('/')
@router.route('/<name>')
async def hello(connection, name='world'):
	return HttpResponse(f"Hello, {name}")


@router.route('/count')
@router.route('/count/<int:number>')
async def count(connection, number=10):
	for i in range(number):
		await connection.send(f'count {i}\n', finish=False)
		await asyncio.sleep(1)
	await connection.send('', finish=True)


@router.route('/ping')
async def echo(connection):
	data = {"message": "pong!"}
	return JsonResponse(data)

app = create_app(routers=[router])