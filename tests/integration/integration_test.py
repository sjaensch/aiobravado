import asyncio
import io
import os.path
import time

import pytest

from aiobravado import aiohttp_client
from aiobravado.client import SwaggerClient
from aiobravado.exception import HTTPBadRequest
from aiobravado.exception import HTTPInternalServerError
from aiobravado.exception import HTTPNotFound


@pytest.fixture
def swagger_client(integration_server, event_loop):
    # Run all integration tests twice, once with our AsyncioClient and once again with the RequestsClient
    # to make sure they both behave the same.
    # Once this integration suite has become stable (i.e. we're happy with the approach and the test coverage)
    # it could move to bravado and test all major HTTP clients (requests, fido, asyncio).
    spec_url = '{}/swagger.yaml'.format(integration_server)
    http_client = aiohttp_client.AiohttpClient(loop=event_loop)
    client = event_loop.run_until_complete(
        SwaggerClient.from_url(
            spec_url,
            http_client=http_client,
            config={'also_return_response': True},
        )
    )
    yield client
    http_client.client_session.close()


@pytest.mark.asyncio
async def test_get_query_args(swagger_client):
    result, response = await swagger_client.user.loginUser(
        username='asyncio',
        password='password',
        invalidate_sessions=True,
    ).result(timeout=1)

    assert result == 'success'
    # let's make sure we can access the headers through the response object
    assert response.headers['X-Rate-Limit'] == '4711'
    assert response.headers['X-Expires-After'] == 'Expiration date'


@pytest.mark.asyncio
async def test_response_headers(swagger_client):
    """Make sure response headers are returned in the same format across HTTP clients. Namely,
    make sure names and values are str, and that it's possible to access headers in a
    case-insensitive manner."""
    _, response = await swagger_client.pet.getPetById(petId=42).result(timeout=1)
    assert response.headers['content-type'] == response.headers['Content-Type'] == 'application/json; charset=utf-8'


@pytest.mark.asyncio
async def test_post_form_data(swagger_client):
    result, _ = await swagger_client.pet.updatePetWithForm(
        petId=12,
        name='Vivi',
        status='sold',
        userId=42,
    ).result(timeout=1)
    assert result is None


@pytest.mark.asyncio
async def test_put_json_body(swagger_client):
    # the test server would raise a 404 if the data didn't match
    result, _ = await swagger_client.pet.updatePet(
        body={
            'id': 42,
            'category': {
                'name': 'extracute',
            },
            'name': 'Lili',
            'photoUrls': [],
            'status': 'sold',
        },
    ).result(timeout=1)

    assert result is None


@pytest.mark.asyncio
async def test_delete_query_args(swagger_client):
    result, _ = await swagger_client.pet.deletePet(petId=5).result(timeout=1)
    assert result is None


@pytest.mark.asyncio
async def test_post_file_upload(swagger_client):
    with open(os.path.join(os.path.dirname(__file__), '../../testing/sample.jpg'), 'rb') as image:
        result, _ = await swagger_client.pet.uploadFile(
            petId=42,
            file=image,
            userId=12,
        ).result(timeout=1)


@pytest.mark.asyncio
async def test_post_file_upload_stream_no_name(swagger_client):
    with open(os.path.join(os.path.dirname(__file__), '../../testing/sample.jpg'), 'rb') as image:
        bytes_io = io.BytesIO(image.read())  # BytesIO has no attribute 'name'
        result, _ = await swagger_client.pet.uploadFile(
            petId=42,
            file=bytes_io,
            userId=12,
        ).result(timeout=1)


@pytest.mark.asyncio
async def test_server_400(swagger_client):
    with pytest.raises(HTTPBadRequest):
        await swagger_client.user.loginUser(username='not', password='correct').result(timeout=1)


@pytest.mark.asyncio
async def test_server_404(swagger_client):
    with pytest.raises(HTTPNotFound):
        await swagger_client.pet.getPetById(petId=5).result(timeout=1)


@pytest.mark.asyncio
async def test_server_500(swagger_client):
    with pytest.raises(HTTPInternalServerError):
        await swagger_client.pet.deletePet(petId=42).result(timeout=1)


# def test_concurrency(integration_server, event_loop):
#     start_time = time.time()
#     event_loop.run_until_complete(_test_asyncio_client(integration_server))
#     end_time = time.time()
#
#     # There are three things being executed asynchronously:
#     # 1. sleep 1 second in the main event loop
#     # 2. fetch the response for client1 (the server sleeps 1 second)
#     # 3. fetch the response for client2 (the server sleeps 1 second)
#     # All of this combined should take only a bit more than one second.
#     # While this assertion could become flaky depending on how busy the system that runs the test
#     # is for now it's a nice confirmation that things work as expected. We can remove it later if
#     # it becomes a problem.
#     assert end_time - start_time < 2


async def sleep_coroutine():
    await asyncio.sleep(1)
    return 42


async def get_swagger_client(spec_url, http_client):
    return await SwaggerClient.from_url(
        spec_url,
        http_client=http_client,
    )


@pytest.mark.asyncio
async def test_asyncio_client(integration_server, event_loop):
    # There are three things being executed asynchronously:
    # 1. sleep 1 second in the main event loop
    # 2. fetch the response for client1 (the server sleeps 1 second)
    # 3. fetch the response for client2 (the server sleeps 1 second)
    # All of this combined should take only a bit more than one second.
    # While this assertion could become flaky depending on how busy the system that runs the test
    # is for now it's a nice confirmation that things work as expected. We can remove it later if
    # it becomes a problem.
    start_time = time.time()

    spec_url = '{}/swagger.yaml'.format(integration_server)
    # schedule our first coroutine (after _test_asyncio_client) in the default event loop
    future = asyncio.ensure_future(sleep_coroutine())
    # more work for the default event loop
    http_client = aiohttp_client.AiohttpClient(loop=event_loop)
    client1 = await get_swagger_client(spec_url, http_client)
    client2 = await get_swagger_client(spec_url.replace('localhost', '127.0.0.1'), http_client)

    # two tasks for the event loop running in a separate thread
    future1 = client1.store.getInventory()
    future2 = client2.store.getInventory()

    result = await future
    assert result == 42

    result1 = await future1.result(timeout=5)
    assert result1 == {}

    result2 = await future2.result(timeout=5)
    assert result2 == {}

    end_time = time.time()
    assert end_time - start_time < 2

    http_client.client_session.close()
