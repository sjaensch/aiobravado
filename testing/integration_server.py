import argparse
import asyncio
import os.path

from aiohttp import web


async def swagger_spec(request):
    with open(os.path.join(os.path.dirname(__file__), 'swagger.yaml')) as f:
        spec = f.read()
    return web.Response(text=spec, content_type='text/vnd.yaml')


async def store_inventory(request):
    await asyncio.sleep(1)
    return web.json_response({})


async def login(request):
    if not (
        request.query.get('username') == 'asyncio'
        and request.query.get('password') == 'password'
        and request.query.get('invalidate_sessions') == 'True'
    ):
        return web.HTTPBadRequest()

    return web.json_response('success', headers={
        'X-Rate-Limit': '4711',
        'X-Expires-After': 'Expiration date',
    })


async def get_pet(request):
    pet_id = request.match_info['petId']
    if pet_id == '5':
        return web.HTTPNotFound()

    return web.json_response({
        'id': int(pet_id),
        'name': 'Lili',
        'photoUrls': [],
    })


async def update_pet_formdata(request):
    post_data = await request.post()
    if not (
        request.match_info['petId'] == '12'
        and post_data.get('name') == 'Vivi'
        and post_data.get('status') == 'sold'
        and request.headers.get('userId') == '42'
    ):
        return web.HTTPNotFound()

    return web.json_response({})


async def upload_pet_image(request):
    with open(os.path.join(os.path.dirname(__file__), 'sample.jpg'), 'rb') as f:
        data = await request.post()
        file_data = data.get('file')
        content = file_data.file.read()
        expected_content = f.read()

    if content != expected_content:
        return web.HTTPBadRequest()

    if not (
        request.match_info['petId'] == '42'
        and data.get('userId') == '12'
    ):
        return web.HTTPBadRequest()

    return web.json_response({})


async def update_pet(request):
    body = await request.json()
    success = body == {
        'id': 42,
        'category': {
            'name': 'extracute',
        },
        'name': 'Lili',
        'photoUrls': [],
        'status': 'sold',
    }

    if success:
        return web.json_response({})

    return web.HTTPBadRequest()


async def delete_pet(request):
    if request.query.get('petId') == '42':
        return web.HTTPInternalServerError()

    return web.json_response({})


def setup_routes(app):
    app.router.add_get('/swagger.yaml', swagger_spec)
    app.router.add_get('/store/inventory', store_inventory)
    app.router.add_get('/user/login', login)
    app.router.add_get('/pet/{petId}', get_pet)
    app.router.add_post('/pet/{petId}', update_pet_formdata)
    app.router.add_post('/pet/{petId}/uploadImage', upload_pet_image)
    app.router.add_put('/pet', update_pet)
    app.router.add_delete('/pet', delete_pet)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--port', dest='port',
        type=int, default=8080,
        help='The port the webserver should listen on (default: %(default)s)',
    )
    args = parser.parse_args()

    app = web.Application()
    setup_routes(app)
    web.run_app(app, host='127.0.0.1', port=args.port)
