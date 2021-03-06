import os

import pika_pydantic
import pika


def test_attributes_of_blocking_channel(connection, TestQueues):
    """Test the channel object has both the pika_pydantic.BlockingChannel attributes and the pika.BlockingChannel attributes"""

    channel = pika_pydantic.BlockingChannel(connection, TestQueues)

    assert hasattr(channel, "listen")
    assert hasattr(channel, "send")

    assert hasattr(channel, "start_consuming")
