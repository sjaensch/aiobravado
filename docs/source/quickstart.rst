Quickstart
==========

Usage
-----

Install the latest stable version from PyPi:

::

    $ pip install --upgrade aiobravado

.. _hello-pet:

Your first Hello World! (or Hello Pet)
--------------------------------------

Here is a simple example to try from a REPL (like IPython):

.. code-block:: python

    from aiobravado.client import SwaggerClient

    client = await SwaggerClient.from_url("http://petstore.swagger.io/v2/swagger.json")
    pet = await client.pet.getPetById(petId=42).result()

If you were lucky, and pet Id with 42 was present, you will get back a result.
It will be a dynamically created instance of ``aiobravado.model.Pet`` with attributes ``category``, etc. You can even try ``pet.category.id`` or ``pet.tags[0]``.

Sample Response: ::

       Pet(category=Category(id=0L, name=u''), status=u'', name=u'', tags=[Tag(id=0L, name=u'')], photoUrls=[u''], id=2)

If you got a ``404``, try some other petId.


Lets try a POST call
--------------------

Here we will demonstrate how ``aiobravado`` hides all the ``JSON`` handling from the user, and makes the code more Pythonic.

.. code-block:: python

        Pet = client.get_model('Pet')
        Category = client.get_model('Category')
        pet = Pet(id=42, name="tommy", category=Category(id=24))
        await client.pet.addPet(body=pet).result()


This is too fancy for me! I want a simple dict response!
--------------------------------------------------------

``aiobravado`` has taken care of that as well. Configure the client to not use models.

.. code-block:: python

        from aiobravado.client import SwaggerClient
        from aiobravado.fido_client import FidoClient

        client = await SwaggerClient.from_url(
            'http://petstore.swagger.io/v2/swagger.json',
            config={'use_models': False}
        )

        result = await client.pet.getPetById(petId=42).result(timeout=4)

``result`` will look something like:

.. code-block:: json

        {
            'category': {
                'id': 0L,
                'name': u''
            },
            'id': 2,
            'name': u'',
            'photoUrls': [u''],
            'status': u'',
            'tags': [
                {'id': 0L, 'name': u''}
            ]
        }
