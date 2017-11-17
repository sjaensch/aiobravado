# -*- coding: utf-8 -*-
"""
Swagger Specification related functional tests
"""
import pytest
from mocket.plugins.httpretty import HTTPretty
from swagger_spec_validator.common import SwaggerValidationError

from aiobravado.client import ResourceDecorator
from aiobravado.client import SwaggerClient
from tests.functional.conftest import API_DOCS_URL
from tests.functional.conftest import register_get
from tests.functional.conftest import register_spec
from tests.functional.conftest import swagger_client


@pytest.mark.asyncio
async def test_invalid_spec_raises_SwaggerValidationError(
        swagger_dict, http_client):
    swagger_dict['paths']['/test_http']['get']['parameters'][0]['type'] = 'X'
    register_spec(swagger_dict)
    with pytest.raises(SwaggerValidationError) as excinfo:
        await swagger_client(http_client)
    assert 'is not valid' in str(excinfo.value)


@pytest.mark.asyncio
async def test_correct_route_with_basePath_as_slash(swagger_dict, http_client):
    register_spec(swagger_dict)
    register_get("http://localhost/test_http?test_param=foo")
    client = await swagger_client(http_client)
    assert await client.api_test.testHTTP(test_param="foo").result() is None


@pytest.mark.asyncio
async def test_basePath_works(swagger_dict, http_client):
    swagger_dict["basePath"] = "/append"
    register_spec(swagger_dict)
    register_get("http://localhost/append/test_http?test_param=foo")
    client = await swagger_client(http_client)
    await client.api_test.testHTTP(test_param="foo").result()
    assert ["foo"] == HTTPretty.last_request.querystring['test_param']


@pytest.mark.asyncio
async def test_resources_are_attrs_on_client(swagger_dict, http_client):
    register_spec(swagger_dict)
    client = await swagger_client(http_client)
    assert isinstance(client.api_test, ResourceDecorator)


@pytest.mark.asyncio
async def test_headers_sendable_with_api_doc_request(swagger_dict, http_client):
    register_spec(swagger_dict)
    await SwaggerClient.from_url(
        API_DOCS_URL,
        http_client=http_client,
        request_headers={'foot': 'bart'},
    )
    assert 'bart' == HTTPretty.last_request.headers.get('foot')


@pytest.mark.asyncio
async def test_hostname_if_passed_overrides_origin_url(swagger_dict, http_client):
    register_get("http://foo/test_http?", body='')
    swagger_dict['host'] = 'foo'
    register_spec(swagger_dict)
    client = await swagger_client(http_client)
    await client.api_test.testHTTP(test_param="foo").result()
    assert ["foo"] == HTTPretty.last_request.querystring['test_param']


@pytest.mark.asyncio
async def test_correct_route_with_basePath_no_slash(swagger_dict, http_client):
    register_get(
        "http://localhost/lame/test/test_http?test_param=foo",
        body=u'""')
    swagger_dict["basePath"] = "/lame/test"
    register_spec(swagger_dict)
    client = await swagger_client(http_client)
    assert await client.api_test.testHTTP(test_param="foo").result() is None
