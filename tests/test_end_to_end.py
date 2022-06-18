import os

import pika_pydantic
import pika
from pydantic import NoneBytes


def test_channels_and_publishers_end_to_end(
    connection, TestQueues, TestData, TestMessage
):
    """Creates two consumers and then tests both publishers."""

    channel = pika_pydantic.BlockingChannel(connection, TestQueues)

    latest = {"data": None, "message": None}

    # Callback for the Data queue
    def data_callback(channel, method, frame, data: TestData):
        latest["data"] = data
        channel.smart_publish(TestQueues.MESSAGE, TestMessage(text="now processed"))

    # Callback for the Message queue
    def message_callback(channel, method, frame, data: TestMessage):
        latest["message"] = data

    # Register two consumers
    channel.smart_consume(TestQueues.MESSAGE, message_callback, auto_ack=True)
    channel.smart_consume(TestQueues.DATA, data_callback, auto_ack=True)

    assert latest["data"] is None
    assert latest["message"] is None

    # Publish on one channel
    channel.smart_publish(TestQueues.MESSAGE, TestMessage(text="some text"))
    connection.process_data_events(time_limit=None)

    assert latest["data"] is None
    assert latest["message"].text == "some text"

    # Publish on data channel that then publishes again on message channel
    channel.smart_publish(TestQueues.DATA, TestData(value=25, elements=["a"]))

    connection.process_data_events(time_limit=None)

    assert latest["data"].value == 25

    connection.process_data_events(time_limit=None)

    assert latest["message"].text == "now processed"
