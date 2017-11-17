import os
import os.path
import subprocess
import time
import urllib

import ephemeral_port_reserve
import pytest


def wait_unit_service_starts(url, timeout=10):
    start = time.time()
    while time.time() < start + timeout:
        try:
            urllib.request.urlopen(url, timeout=2)
        except urllib.error.HTTPError:
            return
        except urllib.error.URLError:
            time.sleep(0.1)


@pytest.fixture(scope='session')
def integration_server():
    script_name = os.path.join(os.path.dirname(__file__), '../../testing/integration_server.py')
    server_port = ephemeral_port_reserve.reserve()
    server = subprocess.Popen(
        ['python', script_name, '-p', str(server_port)],
        stdin=None, stdout=subprocess.DEVNULL, stderr=None,
    )
    wait_unit_service_starts('http://localhost:{port}'.format(port=server_port))

    yield 'http://localhost:{}'.format(server_port)

    server.terminate()
