# Teke

Teke is a lightweight [ASGI](https://asgi.readthedocs.io/en/latest/) framework that you can use to create fast async REST APIs with Python.

## Requirements

Python 3.10+

## Installation

```shell
$ pip install teke
```

You'll also want to install an ASGI server, such as [uvicorn](http://www.uvicorn.org/), [daphne](https://github.com/django/daphne/), or [hypercorn](https://pgjones.gitlab.io/hypercorn/).

```shell
$ pip install "uvicorn[standard]"
```

## Example

**example.py**:

```python
from teke import JsonResponse, Router, create_app

router = Router()

@router.route("/hello/<name>")
async def hello(connection, name):
    return JsonResponse({"hello": name})

app = create_app(routers=[router])
```

Then run the application using Uvicorn:

```shell
$ uvicorn example:app
```

Run uvicorn with `--reload` to enable auto-reloading on code changes.

For a more complete example, see examples[here](https://github.com/mrkiura/teke/examples).

## Coming soon:
* WebSocket support
* Lifecycle hooks
* CORS middleware

## Dependencies

teke depends on the following python packages:
* anyio
* uvloop
* Werkzeug
