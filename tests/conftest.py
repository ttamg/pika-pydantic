import os
import random
import string
from typing import List

import pika
import pika_pydantic
import pytest


@pytest.fixture
def connection():
    PIKA_URL = os.environ.get("PIKA_URL", "amqp://guest:guest@localhost:5672/")
    parameters = pika.URLParameters(PIKA_URL)
    connection = pika.BlockingConnection(parameters)
    return connection


@pytest.fixture
def TestMessage():
    class TestMessage(pika_pydantic.BaseModel):
        text: str

    return TestMessage


@pytest.fixture
def TestData():
    class TestData(pika_pydantic.BaseModel):
        value: int
        elements: List[str]

    return TestData


@pytest.fixture(scope="function")
def TestQueues(TestMessage, TestData):
    class TestQueues(pika_pydantic.Queues):
        MESSAGE = TestMessage
        DATA = TestData

    return TestQueues
