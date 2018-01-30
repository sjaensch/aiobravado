# -*- coding: utf-8 -*-
import functools
import json

import pytest
import yaml
from bravado_asyncio.http_client import AsyncioClient
from bravado_asyncio.http_client import RunMode
from mocket.mocket import Mocketizer
from mocket.plugins.httpretty import HTTPretty

from aiobravado.client import SwaggerClient


API_DOCS_URL = "http://localhost/api-docs"

# Convenience for httpretty.register_uri(httpretty.GET, **kwargs)
register_get = functools.partial(HTTPretty.register_uri, HTTPretty.GET, content_type='application/json')


def register_spec(swagger_dict, response_spec=None, spec_type='json'):
    if response_spec is not None:
        response_specs = swagger_dict['paths']['/test_http']['get']['responses']
        response_specs['200']['schema'] = response_spec

    if spec_type == 'yaml':
        serialize_function = yaml.dump
        content_type = 'application/yaml'
    else:
        serialize_function = json.dumps
        content_type = 'application/json'
    headers = 'Content-Type: {0}'.format(content_type)
    register_get(
        API_DOCS_URL,
        body=serialize_function(swagger_dict),
        headers=headers,
    )


@pytest.fixture
def swagger_dict():
    parameter = {
        "in": "query",
        "name": "test_param",
        "type": "string"
    }
    responses = {
        "200": {
            "description": "Success"
        }
    }
    operation = {
        "operationId": "testHTTP",
        "parameters": [parameter],
        "responses": responses,
        "tags": ["api_test"],
    }
    paths = {
        "/test_http": {
            "get": operation
        }
    }
    return {
        "swagger": "2.0",
        "info": {
            "version": "1.0.0",
            "title": "Simple"
        },
        "basePath": "/",
        "paths": paths
    }


@pytest.fixture(autouse=True)
def httprettified():
    with Mocketizer(instance=None):
        yield


@pytest.fixture
def http_client(event_loop):
    http_client = AsyncioClient(loop=event_loop, run_mode=RunMode.FULL_ASYNCIO)
    yield http_client
    http_client.client_session.close()


# This function can't be a fixture right now since we need to register the URLs before creating the client
async def swagger_client(http_client):
    return await SwaggerClient.from_url(
        API_DOCS_URL,
        http_client=http_client,
    )
