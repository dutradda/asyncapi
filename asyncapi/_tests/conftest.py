import asynctest
import orjson
import pytest

import asyncapi.builder


@pytest.fixture
def spec_dict():
    return {
        'info': {
            'title': 'Fake API',
            'version': '0.0.1',
            'description': 'Faked API',
        },
        'servers': {
            'development': {
                'url': 'fake.fake',
                'protocol': 'kafka',
                'description': 'Fake Server',
            }
        },
        'channels': {
            'fake': {
                'description': 'Fake Channel',
                'subscribe': {
                    'operationId': 'fake_operation',
                    'message': {'$ref': '#/components/messages/FakeMessage'},
                },
            }
        },
        'components': {
            'messages': {
                'FakeMessage': {
                    'name': 'Fake Message',
                    'title': 'Faked',
                    'summary': 'Faked message',
                    'contentType': 'application/json',
                    'payload': {'$ref': '#/components/schemas/FakePayload'},
                }
            },
            'schemas': {
                'FakePayload': {
                    'type': 'object',
                    'properties': {'faked': {'type': 'integer'}},
                }
            },
        },
    }


@pytest.fixture(autouse=True)
def fake_yaml(mocker, spec_dict):
    yaml = mocker.patch.object(asyncapi.builder, 'yaml')
    mocker.patch('asyncapi.builder.open')
    yaml.safe_load.return_value = spec_dict
    return yaml


@pytest.fixture(autouse=True)
def fake_broadcast(json_message, mocker, async_iterator):
    broadcast = mocker.patch.object(asyncapi.builder, 'Broadcast').return_value
    broadcast.publish = asynctest.CoroutineMock()
    broadcast.connect = asynctest.CoroutineMock()
    broadcast.subscribe.return_value = async_iterator(
        [mocker.MagicMock(message=json_message)]
    )
    return broadcast


@pytest.fixture
def fake_message(fake_api):
    return fake_api.spec.channels['fake'].subscribe.message.payload(1)


@pytest.fixture
def json_message():
    return orjson.dumps({'faked': 1})


@pytest.fixture
def json_invalid_message():
    return orjson.dumps({'faked': 'invalid'})


@pytest.fixture
def async_iterator(mocker):
    return AsyncIterator


class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...
