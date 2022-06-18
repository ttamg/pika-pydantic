import random
import string
import time

from .models import CollectedData, Message
from .queues import Queues

"""
Consumer prints the message and then simulates fetching some data from an API
"""


def consumer_1(channel, method, frame, data: Message):

    print(
        f"Consumer 1 received message with text ({data.text}).  Now fetching data ..."
    )

    # Simulate fetching data
    time.sleep(2)

    data = [random.choice(string.ascii_lowercase) for i in range(random.randint(1, 10))]
    print(f"Data collected - {data}")

    # Producer send to data queue
    collected_data = CollectedData(data=data, counter=len(data))
    channel.send(Queues.PROCESS_DATA, collected_data)

    # Finally acknowledge using standard pika
    channel.basic_ack(method.delivery_tag)

    print(f"Consumer 1 done.")
