# -*- coding: utf-8 -*-
"""
Request related functional tests
"""
import pytest
from mocket.plugins.httpretty import HTTPretty
from six.moves import cStringIO
from six.moves.urllib import parse as urlparse

from tests.functional.conftest import register_get
from tests.functional.conftest import register_spec
from tests.functional.conftest import swagger_client


@pytest.mark.xfail(reason='Fails with aiohttp 3 due to https://github.com/mindflayer/python-mocket/issues/66')
@pytest.mark.asyncio
async def test_form_params_in_request(swagger_dict, http_client):
    param1_spec = {
        'in': 'formData',
        'name': 'param_id',
        'type': 'integer'
    }
    param2_spec = {
        'in': 'formData',
        'name': 'param_name',
        'type': 'string'
    }
    path_spec = swagger_dict['paths']['/test_http']
    path_spec['post'] = path_spec.pop('get')
    path_spec['post']['parameters'] = [param1_spec, param2_spec]
    register_spec(swagger_dict)
    HTTPretty.register_uri(HTTPretty.POST, 'http://localhost/test_http')
    client = await swagger_client(http_client)
    await client.api_test.testHTTP(param_id=42, param_name='foo').result()
    content_type = HTTPretty.last_request.headers['content-type']
    assert 'application/x-www-form-urlencoded' == content_type
    body = urlparse.parse_qs(HTTPretty.last_request.body)
    assert {b'param_name': [b'foo'], b'param_id': [b'42']} == body


@pytest.mark.xfail(reason='mocket library does not handle request correctly')
@pytest.mark.asyncio
async def test_file_upload_in_request(swagger_dict, http_client):
    param1_spec = {
        'in': 'formData',
        'name': 'param_id',
        'type': 'integer'
    }
    param2_spec = {
        'in': 'formData',
        'name': 'file_name',
        'type': 'file'
    }
    path_spec = swagger_dict['paths']['/test_http']
    path_spec['post'] = path_spec.pop('get')
    path_spec['post']['parameters'] = [param1_spec, param2_spec]
    path_spec['post']['consumes'] = ['multipart/form-data']
    register_spec(swagger_dict)
    HTTPretty.register_uri(HTTPretty.POST, 'http://localhost/test_http?')
    client = await swagger_client(http_client)
    await client.api_test.testHTTP(param_id=42, file_name=cStringIO('boo')).result()
    content_type = HTTPretty.last_request.headers['content-type']

    assert content_type.startswith('multipart/form-data')
    assert b'42' in HTTPretty.last_request.body
    assert b'boo' in HTTPretty.last_request.body


@pytest.mark.asyncio
async def test_parameter_in_path_of_request(swagger_dict, http_client):
    path_param_spec = {
        'in': 'path',
        'name': 'param_id',
        'required': True,
        'type': 'string',
    }
    paths_spec = swagger_dict['paths']
    paths_spec['/test_http/{param_id}'] = paths_spec.pop('/test_http')
    paths_spec['/test_http/{param_id}']['get']['parameters'].append(
        path_param_spec)
    register_spec(swagger_dict)
    register_get('http://localhost/test_http/42?test_param=foo')
    client = await swagger_client(http_client)
    assert await client.api_test.testHTTP(test_param='foo', param_id='42').result() is None


@pytest.mark.asyncio
async def test_default_value_not_in_request(swagger_dict, http_client):
    # Default should be applied on the server side so no need to send it in
    # the request.
    swagger_dict['paths']['/test_http']['get']['parameters'][0]['default'] = 'X'
    register_spec(swagger_dict)
    register_get('http://localhost/test_http?')
    client = await swagger_client(http_client)
    await client.api_test.testHTTP().result()
    assert 'test_param' not in HTTPretty.last_request.querystring


@pytest.mark.asyncio
async def test_array_with_collection_format_in_path_of_request(
        swagger_dict, http_client):
    path_param_spec = {
        'in': 'path',
        'name': 'param_ids',
        'type': 'array',
        'items': {
            'type': 'integer'
        },
        'collectionFormat': 'csv',
        'required': True,
    }
    swagger_dict['paths']['/test_http/{param_ids}'] = \
        swagger_dict['paths'].pop('/test_http')
    swagger_dict['paths']['/test_http/{param_ids}']['get']['parameters'] = \
        [path_param_spec]
    register_spec(swagger_dict)
    register_get('http://localhost/test_http/40,41,42')
    client = await swagger_client(http_client)
    assert await client.api_test.testHTTP(param_ids=[40, 41, 42]).result() is None
