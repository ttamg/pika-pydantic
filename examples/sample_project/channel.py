import pika_pydantic
import pika

from .queues import Queues


def open_channel():
    """Creates a new channel and connection"""

    parameters = pika.URLParameters("amqp://guest:guest@localhost:5672/")

    connection = pika.BlockingConnection(parameters)

    channel = pika_pydantic.BlockingChannel(connection=connection, queues=Queues)

    channel.basic_qos(prefetch_count=1)

    return channel


# The same connection can only be used within the same thread.
channel = open_channel()
