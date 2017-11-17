# -*- coding: utf-8 -*-
from functools import partial

import pytest
from bravado_core.exception import MatchingResponseNotFound
from bravado_core.operation import Operation
from bravado_core.response import IncomingResponse
from mock import Mock
from mock import patch

from aiobravado.exception import HTTPError
from aiobravado.http_future import unmarshal_response


def unmarshal_response_inner_factory(result):
    async def mock_umi(*args, **kwargs):
        return result
    return mock_umi


def test_5XX(event_loop):
    incoming_response = Mock(spec=IncomingResponse, status_code=500)
    operation = Mock(spec=Operation)
    with pytest.raises(HTTPError) as excinfo:
        event_loop.run_until_complete(unmarshal_response(incoming_response, operation))
    assert excinfo.value.response.status_code == 500


@patch('aiobravado.http_future.unmarshal_response_inner', new_callable=partial(unmarshal_response_inner_factory, 99))
def test_2XX(_1, event_loop):
    incoming_response = Mock(spec=IncomingResponse)
    incoming_response.status_code = 200
    operation = Mock(spec=Operation)
    event_loop.run_until_complete(unmarshal_response(incoming_response, operation))
    assert incoming_response.swagger_result == 99


@patch('aiobravado.http_future.unmarshal_response_inner',
       side_effect=MatchingResponseNotFound('boo'))
def test_2XX_matching_response_not_found_in_spec(_1, event_loop):
    incoming_response = Mock(spec=IncomingResponse, status_code=200)
    operation = Mock(spec=Operation)
    with pytest.raises(HTTPError) as excinfo:
        event_loop.run_until_complete(unmarshal_response(incoming_response, operation))
    assert excinfo.value.response.status_code == 200
    assert excinfo.value.message == 'boo'


@patch('aiobravado.http_future.unmarshal_response_inner',
       side_effect=MatchingResponseNotFound)
def test_4XX_matching_response_not_found_in_spec(_1, event_loop):
    incoming_response = Mock(spec=IncomingResponse, status_code=404)
    operation = Mock(spec=Operation)
    with pytest.raises(HTTPError) as excinfo:
        event_loop.run_until_complete(unmarshal_response(incoming_response, operation))
    assert excinfo.value.response.status_code == 404


@patch(
    'aiobravado.http_future.unmarshal_response_inner',
    new_callable=partial(unmarshal_response_inner_factory, {'msg': 'Not found'})
)
def test_4XX(_1, event_loop):
    incoming_response = Mock(spec=IncomingResponse, status_code=404)
    operation = Mock(spec=Operation)
    with pytest.raises(HTTPError) as excinfo:
        event_loop.run_until_complete(unmarshal_response(incoming_response, operation))
    assert excinfo.value.response.status_code == 404
    assert excinfo.value.swagger_result == {'msg': 'Not found'}


@patch('aiobravado.http_future.unmarshal_response_inner', new_callable=partial(unmarshal_response_inner_factory, 99))
def test_response_callbacks_executed_on_happy_path(_1, event_loop):
    incoming_response = Mock(spec=IncomingResponse)
    incoming_response.status_code = 200
    operation = Mock(spec=Operation)
    callback = Mock()
    event_loop.run_until_complete(
        unmarshal_response(incoming_response, operation, response_callbacks=[callback])
    )
    assert incoming_response.swagger_result == 99
    assert callback.call_count == 1


@patch('aiobravado.http_future.unmarshal_response_inner', new_callable=partial(unmarshal_response_inner_factory, 99))
def test_response_callbacks_executed_on_failure(_1, event_loop):
    incoming_response = Mock(spec=IncomingResponse, status_code=404)
    operation = Mock(spec=Operation)
    callback = Mock()
    with pytest.raises(HTTPError) as excinfo:
        event_loop.run_until_complete(
            unmarshal_response(incoming_response, operation, response_callbacks=[callback])
        )
    assert excinfo.value.response.status_code == 404
    assert callback.call_count == 1
