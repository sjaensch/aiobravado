# -*- coding: utf-8 -*-
import mock
import pytest
from aiohttp import ClientResponse

from aiobravado.exception import HTTPError
from aiobravado.exception import HTTPInternalServerError
from aiobravado.exception import HTTPServerError
from aiobravado.exception import make_http_exception
from aiobravado.aiohttp_client import AioHTTPResponseAdapter, AsyncioResponse


@pytest.fixture
def response_500():
    mocked_response = mock.Mock(autospec=ClientResponse)
    mocked_response.status = 500
    mocked_response.reason = 'Server Error'

    return AsyncioResponse(
        response=mocked_response,
        remaining_timeout=1,
    )


def test_response_only(response_500):
    incoming_response = AioHTTPResponseAdapter(response_500)
    assert str(HTTPError(incoming_response)) == '500 Server Error'


def test_response_and_message(response_500):
    incoming_response = AioHTTPResponseAdapter(response_500)
    actual = str(HTTPError(incoming_response, message='Kaboom'))
    assert actual == '500 Server Error: Kaboom'


def test_response_and_swagger_result(response_500):
    incoming_response = AioHTTPResponseAdapter(response_500)
    actual = str(HTTPError(incoming_response, swagger_result={'msg': 'Kaboom'}))
    assert actual == "500 Server Error: {'msg': 'Kaboom'}"


def test_response_and_message_and_swagger_result(response_500):
    incoming_response = AioHTTPResponseAdapter(response_500)
    actual = str(HTTPError(
        incoming_response,
        message="Holy moly!",
        swagger_result={'msg': 'Kaboom'}))
    assert actual == "500 Server Error: Holy moly!: {'msg': 'Kaboom'}"


def test_make_http_exception(response_500):
    incoming_response = AioHTTPResponseAdapter(response_500)
    exc = make_http_exception(
        incoming_response,
        message="Holy moly!",
        swagger_result={'msg': 'Kaboom'}
    )
    assert isinstance(exc, HTTPError)
    assert isinstance(exc, HTTPServerError)
    assert type(exc) == HTTPInternalServerError
    assert str(exc) == "500 Server Error: Holy moly!: {'msg': 'Kaboom'}"


def test_make_http_exception_unknown():
    mocked_response = mock.Mock(autospec=ClientResponse)
    mocked_response.status = 600
    mocked_response.reason = 'Womp Error'
    exc = make_http_exception(
        AioHTTPResponseAdapter(mocked_response),
    )
    assert type(exc) == HTTPError
