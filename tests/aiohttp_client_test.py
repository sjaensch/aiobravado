import mock
import pytest

from aiobravado.aiohttp_client import AiohttpClient


@pytest.fixture(autouse=True)
def mock_ensure_future():
    with mock.patch('asyncio.ensure_future') as mocked_ensure_future:
        yield mocked_ensure_future


@pytest.fixture
def mock_client_session():
    return mock.Mock(name='client session')


@pytest.fixture
def aiohttp_client(mock_client_session):
    return AiohttpClient(client_session=mock_client_session)


@pytest.fixture
def request_params():
    return {
        'method': 'GET',
        'url': 'http://swagger.py/client-test',
        'headers': {},
    }


def test_simple_get(aiohttp_client, mock_client_session, request_params):
    request_params['params'] = {'foo': 'bar'}

    aiohttp_client.request(request_params)

    mock_client_session.request.assert_called_once_with(
        method=request_params['method'],
        url=request_params['url'],
        params=request_params['params'],
        data=mock.ANY,
        headers={},
    )
    assert mock_client_session.request.call_args[1]['data']._fields == []


def test_int_param(aiohttp_client, mock_client_session, request_params):
    request_params['params'] = {'foo': 5}

    aiohttp_client.request(request_params)
    assert mock_client_session.request.call_args[1]['params'] == {'foo': '5'}


@pytest.mark.parametrize(
    'param_name, param_value, expected_param_value',
    (
        ('foo', 'bar', 'bar'),
        ('answer', 42, '42'),
        ('answer', False, 'False'),
        ('answer', None, 'None'),  # do we want this?
    )
)
def test_formdata(aiohttp_client, mock_client_session, request_params, param_name, param_value, expected_param_value):
    request_params['data'] = {param_name: param_value}

    aiohttp_client.request(request_params)

    mock_client_session.request.assert_called_once_with(
        method=request_params['method'],
        url=request_params['url'],
        params=None,
        data=mock.ANY,
        headers={},
    )

    field_data = mock_client_session.request.call_args[1]['data']._fields[0]
    assert field_data[0]['name'] == param_name
    assert field_data[2] == expected_param_value


def test_file_data(aiohttp_client, mock_client_session, request_params):
    class FileObj:
        name = 'foo'

    request_params['method'] = 'POST'
    request_params['files'] = [('picture', ('filename', FileObj))]

    aiohttp_client.request(request_params)

    field_data = mock_client_session.request.call_args[1]['data']._fields[0]
    assert field_data[0]['name'] == 'picture'
    assert field_data[0]['filename'] == 'filename'
    assert field_data[2] == FileObj


def test_file_data_int_filename(aiohttp_client, mock_client_session, request_params):
    class FileObj:
        name = 42
        read = mock.Mock()

    request_params['method'] = 'POST'
    request_params['files'] = [('picture', ('filename', FileObj))]

    aiohttp_client.request(request_params)

    field_data = mock_client_session.request.call_args[1]['data']._fields[0]
    assert field_data[0]['name'] == 'picture'
    assert field_data[0]['filename'] == 'filename'
    assert field_data[2] == FileObj.read.return_value
