# -*- coding: utf-8 -*-
import pytest
from bravado_core.operation import Operation
from bravado_core.response import IncomingResponse
from mock import Mock
from mock import patch

from aiobravado.exception import HTTPError
from aiobravado.http_future import FutureAdapter
from aiobravado.http_future import HttpFuture


@pytest.fixture
def mock_future_adapter():
    async def result(timeout=None):
        pass
    return Mock(spec=FutureAdapter, result=result, timeout_errors=None)


@pytest.fixture
def mock_unmarshal_response():
    async def unmarshal_response(*args, **kwargs):
        pass

    with patch('aiobravado.http_future.unmarshal_response', new=unmarshal_response) as _mock:
        yield _mock


def test_200_get_swagger_spec(mock_future_adapter, event_loop):
    response_adapter_instance = Mock(spec=IncomingResponse, status_code=200)
    response_adapter_type = Mock(return_value=response_adapter_instance)
    http_future = HttpFuture(
        future=mock_future_adapter,
        response_adapter=response_adapter_type)

    assert response_adapter_instance == event_loop.run_until_complete(http_future.result())


def test_500_get_swagger_spec(mock_future_adapter, event_loop):
    response_adapter_instance = Mock(spec=IncomingResponse, status_code=500)
    response_adapter_type = Mock(return_value=response_adapter_instance)

    with pytest.raises(HTTPError) as excinfo:
        event_loop.run_until_complete(
            HttpFuture(
                future=mock_future_adapter,
                response_adapter=response_adapter_type,
            ).result()
        )

    assert excinfo.value.response.status_code == 500


def test_200_service_call(mock_unmarshal_response, mock_future_adapter, event_loop):
    response_adapter_instance = Mock(
        spec=IncomingResponse,
        status_code=200,
        swagger_result='hello world')

    response_adapter_type = Mock(return_value=response_adapter_instance)

    http_future = HttpFuture(
        future=mock_future_adapter,
        response_adapter=response_adapter_type,
        operation=Mock(spec=Operation))

    assert 'hello world' == event_loop.run_until_complete(http_future.result())


@patch('aiobravado.http_future.unmarshal_response', autospec=True)
def test_400_service_call(mock_unmarshal_response, mock_future_adapter, event_loop):
    response_adapter_instance = Mock(
        spec=IncomingResponse,
        status_code=400,
        swagger_result={'error': 'Blah'})
    mock_unmarshal_response.side_effect = HTTPError(response_adapter_instance)
    response_adapter_type = Mock(return_value=response_adapter_instance)

    http_future = HttpFuture(
        future=mock_future_adapter,
        response_adapter=response_adapter_type,
        operation=Mock(spec=Operation))

    with pytest.raises(HTTPError) as excinfo:
        event_loop.run_until_complete(http_future.result())
    assert excinfo.value.response.status_code == 400


def test_also_return_response_true(mock_unmarshal_response, mock_future_adapter, event_loop):
    # Verify HTTPFuture(..., also_return_response=True).result()
    # returns the (swagger_result, http_response) and not just swagger_result
    response_adapter_instance = Mock(
        spec=IncomingResponse,
        status_code=200,
        swagger_result='hello world')
    response_adapter_type = Mock(return_value=response_adapter_instance)

    http_future = HttpFuture(
        future=mock_future_adapter,
        response_adapter=response_adapter_type,
        operation=Mock(spec=Operation),
        also_return_response=True)

    swagger_result, http_response = event_loop.run_until_complete(http_future.result())

    assert http_response == response_adapter_instance
    assert swagger_result == 'hello world'
