.. image:: https://img.shields.io/travis/sjaensch/aiobravado.svg
  :target: https://travis-ci.org/sjaensch/aiobravado?branch=master

.. image:: https://img.shields.io/coveralls/sjaensch/aiobravado.svg
  :target: https://coveralls.io/r/sjaensch/aiobravado

.. image:: https://img.shields.io/pypi/v/aiobravado.svg
    :target: https://pypi.python.org/pypi/aiobravado/
    :alt: PyPi version

.. image:: https://img.shields.io/pypi/pyversions/aiobravado.svg
    :target: https://pypi.python.org/pypi/aiobravado/
    :alt: Supported Python versions

Aiobravado
==========

About
-----

Aiobravado is the asyncio version of the `bravado library <https://github.com/Yelp/bravado>`__
for use with the `OpenAPI Specification <https://github.com/OAI/OpenAPI-Specification>`__ (previously
known as Swagger).

aiobravado requires Python 3.5+ and allows you to use asynchronous programming when interacting with OpenAPI-enabled
services. Here's the breakdown of bravado packages and their use case:

- `bravado <https://github.com/Yelp/bravado>`__ - Library to dynamically interact with OpenAPI/Swagger-enabled services. Supports Python 2.7+.
- `fido <https://github.com/Yelp/fido>`__ - HTTP client to enable asynchronous network requests for bravado. Supports Python 2.7+. Depends on twisted. Spins up a separate thread to handle network requests.
- `bravado-asyncio <https://github.com/sjaensch/bravado-asyncio>`__ - asyncio-powered asynchronous HTTP client for bravado. Requires Python 3.5+. It is the default HTTP client for aiobravado, but can be used with bravado as well.
- aiobravado - asyncio-enabled library to dynamically interact with OpenAPI/Swagger-enabled services. Supports basically all of the features of bravado. Requires Python 3.5+. No additional threads are created.

Example Usage
-------------

.. code-block:: Python

    from aiobravado.client import SwaggerClient
    client = await SwaggerClient.from_url('http://petstore.swagger.io/v2/swagger.json')
    pet = await client.pet.getPetById(petId=42).result(timeout=5)

Documentation
-------------

More documentation is available at http://aiobravado.readthedocs.org

Installation
------------

.. code-block:: bash

    # To install aiobravado
    $ pip install aiobravado

    # To install aiobravado with optional packages recommended by aiohttp
    $ pip install aiobravado[aiohttp_extras]

Development
===========

Code is documented using `Sphinx <http://sphinx-doc.org/>`__.

`virtualenv <http://virtualenv.readthedocs.org/en/latest/virtualenv.html>`__ is
recommended to keep dependencies and libraries isolated.

Setup
-----

.. code-block:: bash

    # Run tests
    tox

    # Install git pre-commit hooks
    tox -e pre-commit install

Contributing
------------

1. Fork it ( http://github.com/sjaensch/aiobravado/fork )
2. Create your feature branch (``git checkout -b my-new-feature``)
3. Add your modifications
4. Add short summary of your modifications on ``changelog.rst`` under ``Upcoming release``. Add that entry at the top of the file if it's not there yet.
5. Commit your changes (``git commit -m "Add some feature"``)
6. Push to the branch (``git push origin my-new-feature``)
7. Create new Pull Request

License
-------

Copyright (c) 2013, Digium, Inc. All rights reserved.
Copyright (c) 2014-2015, Yelp, Inc. All rights reserved.

Aiobravado is licensed with a `BSD 3-Clause License <http://opensource.org/licenses/BSD-3-Clause>`__.
