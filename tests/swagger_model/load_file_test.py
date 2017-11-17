# -*- coding: utf-8 -*-
import pytest

from aiobravado.swagger_model import load_file


@pytest.mark.asyncio
async def test_success():
    spec_json = await load_file('test-data/2.0/simple/swagger.json')
    assert '2.0' == spec_json['swagger']


@pytest.mark.parametrize(
    'filename',
    (
        ('test-data/2.0/simple/swagger.yaml'),
        ('test-data/2.0/petstore/swagger.yaml'),
    ),
)
@pytest.mark.asyncio
async def test_success_yaml(filename):
    spec_yaml = await load_file(filename)
    assert '2.0' == spec_yaml['swagger']


@pytest.mark.asyncio
async def test_spec_internal_representation_identical():
    spec_json = await load_file('test-data/2.0/petstore/swagger.json')
    spec_yaml = await load_file('test-data/2.0/petstore/swagger.yaml')

    assert spec_yaml == spec_json


@pytest.mark.asyncio
async def test_non_existent_file():
    with pytest.raises(IOError) as excinfo:
        await load_file('test-data/2.0/i_dont_exist.json')
    assert 'No such file or directory' in str(excinfo.value)
