# -*- coding: utf-8 -*-
"""
Response related functional tests
"""
import datetime
import functools

import pytest
from jsonschema.exceptions import ValidationError

from aiobravado.compat import json
from aiobravado.exception import HTTPError
from tests.functional.conftest import register_get
from tests.functional.conftest import register_spec
from tests.functional.conftest import swagger_client


register_test_http = functools.partial(
    register_get,
    'http://localhost/test_http?test_param=foo')


async def assert_result(expected_result, http_client):
    client = await swagger_client(http_client)
    assert expected_result == await client.api_test.testHTTP(test_param='foo').result()


async def assert_raises_and_matches(exc_type, match_str, http_client):
    client = await swagger_client(http_client)
    with pytest.raises(exc_type) as excinfo:
        await client.api_test.testHTTP(test_param='foo').result()
    assert match_str in str(excinfo.value)


@pytest.mark.asyncio
async def test_500_error_raises_HTTPError(swagger_dict, http_client):
    register_spec(swagger_dict)
    register_get('http://localhost/test_http?test_param=foo', status=500)
    await assert_raises_and_matches(HTTPError, '500 Internal Server Error', http_client)


@pytest.mark.parametrize(
    'rtype, rvalue',
    (
        ('string', '"test"'),
        ('integer', 42),
        ('number', 3.4),
        ('boolean', True),
    )
)
@pytest.mark.asyncio
async def test_primitive_types_returned_in_response(rtype, rvalue, swagger_dict, http_client):
    register_spec(swagger_dict, {'type': rtype})
    register_test_http(body=json.dumps(rvalue))
    await assert_result(rvalue, http_client)


@pytest.mark.parametrize(
    'rtype, rvalue',
    (
        ('string', 42),
        ('integer', 3.4),
        ('number', 'foo'),
        ('boolean', '"NOT BOOL"'),
    )
)
@pytest.mark.asyncio
async def test_invalid_primitive_types_in_response_raises_ValidationError(
        rtype, rvalue, swagger_dict, http_client):
    register_spec(swagger_dict, {'type': rtype})
    register_test_http(body=json.dumps(rvalue))
    await assert_raises_and_matches(ValidationError, "is not of type '{}'".format(rtype), http_client)


@pytest.mark.asyncio
async def test_unstructured_json_in_response(swagger_dict, http_client):
    response_spec = {'type': 'object', 'additionalProperties': True}
    register_spec(swagger_dict, response_spec)
    register_test_http(body='{"some_foo": "bar"}')
    await assert_result({'some_foo': 'bar'}, http_client)


@pytest.mark.asyncio
async def test_date_format_in_reponse(swagger_dict, http_client):
    response_spec = {'type': 'string', 'format': 'date'}
    register_spec(swagger_dict, response_spec)
    register_test_http(body=json.dumps("2014-06-10"))
    await assert_result(datetime.date(2014, 6, 10), http_client)


@pytest.mark.asyncio
async def test_array_in_response(swagger_dict, http_client):
    response_spec = {
        'type': 'array',
        'items': {
            'type': 'string',
        },
    }
    register_spec(swagger_dict, response_spec)
    expected_array = ['inky', 'dinky', 'doo']
    register_test_http(body=json.dumps(expected_array))
    await assert_result(expected_array, http_client)
