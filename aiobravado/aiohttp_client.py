import asyncio
import concurrent.futures
import logging
import time
from collections import Mapping
from typing import NamedTuple
from typing import Optional

import aiohttp
from bravado_core.response import IncomingResponse
from aiohttp.formdata import FormData

from aiobravado.http_client import HttpClient
from aiobravado.http_future import FutureAdapter
from aiobravado.http_future import HttpFuture


log = logging.getLogger(__name__)


AsyncioResponse = NamedTuple(
    'AsyncioResponse', [
        ('response', aiohttp.ClientResponse),
        ('remaining_timeout', Optional[float])
    ]
)


client_session = None


def get_client_session(loop=None):
    global client_session
    if client_session:
        return client_session
    client_session = aiohttp.ClientSession(loop=loop)
    return client_session


class AioHTTPResponseAdapter(IncomingResponse):
    """Wraps a aiohttp Response object to provide a bravado-like interface
    to the response innards.
    """

    def __init__(self, response: AsyncioResponse) -> None:
        self._delegate = response.response
        self._remaining_timeout = response.remaining_timeout

    @property
    def status_code(self):
        return self._delegate.status

    @property
    async def text(self):
        return await asyncio.wait_for(self._delegate.text(), timeout=self._remaining_timeout)

    @property
    async def raw_bytes(self):
        return await asyncio.wait_for(self._delegate.read(), timeout=self._remaining_timeout)

    @property
    def reason(self):
        return self._delegate.reason

    @property
    def headers(self):
        return self._delegate.headers

    async def json(self, **_):
        return await asyncio.wait_for(self._delegate.json(), timeout=self._remaining_timeout)


class AiohttpClient(HttpClient):
    """Asynchronous HTTP client using the asyncio event loop.
    """

    def __init__(self, client_session: aiohttp.ClientSession=None, loop: asyncio.AbstractEventLoop=None) -> None:
        if client_session:
            self.client_session = client_session
        elif loop:
            self.client_session = aiohttp.ClientSession(loop=loop)
        else:
            self.client_session = get_client_session()

    def request(self, request_params, operation=None, response_callbacks=None,
                also_return_response=False):
        """Sets up the request params as per Twisted Agent needs.
        Sets up crochet and triggers the API request in background

        :param request_params: request parameters for the http request.
        :type request_params: dict
        :param operation: operation that this http request is for. Defaults
            to None - in which case, we're obviously just retrieving a Swagger
            Spec.
        :type operation: :class:`bravado_core.operation.Operation`
        :param response_callbacks: List of callables to post-process the
            incoming response. Expects args incoming_response and operation.
        :param also_return_response: Consult the constructor documentation for
            :class:`aiobravado.http_future.HttpFuture`.

        :rtype: :class: `bravado_core.http_future.HttpFuture`
        """

        orig_data = request_params.get('data', {})
        if isinstance(orig_data, Mapping):
            data = FormData()
            for name, value in orig_data.items():
                data.add_field(name, str(value))
        else:
            data = orig_data

        if isinstance(data, FormData):
            for name, file_tuple in request_params.get('files', []):
                stream_obj = file_tuple[1]
                if not hasattr(stream_obj, 'name') or not isinstance(stream_obj.name, str):
                    # work around an issue in aiohttp: it's not able to deal with names of type int. We've observed
                    # this case in the real world and it is a documented possibility:
                    # https://docs.python.org/3/library/io.html#raw-file-i-o
                    stream_obj = stream_obj.read()

                data.add_field(name, stream_obj, filename=file_tuple[0])

        params = self.prepare_params(request_params.get('params'))
        coroutine = self.client_session.request(
            method=request_params.get('method') or 'GET',
            url=request_params.get('url'),
            params=params,
            data=data,
            headers=request_params.get('headers'),
        )

        future = asyncio.ensure_future(coroutine)

        return HttpFuture(
            AsyncioFutureAdapter(future),
            AioHTTPResponseAdapter,
            operation,
            response_callbacks,
            also_return_response,
        )

    def prepare_params(self, params):
        if not params:
            return params

        prepared_params = {
            name: str(value) for name, value in params.items()
        }
        return prepared_params


class AsyncioFutureAdapter(FutureAdapter):

    timeout_errors = (asyncio.TimeoutError,)

    def __init__(self, future: concurrent.futures.Future) -> None:
        self.future = future

    async def result(self, timeout: Optional[float]=None) -> AsyncioResponse:
        start = time.time()
        response = await asyncio.wait_for(self.future, timeout=timeout)
        time_elapsed = time.time() - start
        remaining_timeout = timeout - time_elapsed if timeout else None

        return AsyncioResponse(response=response, remaining_timeout=remaining_timeout)
