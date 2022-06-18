import time

from .models import CollectedData

"""
Consumer gets the data and simulates processing it
"""


def consumer_2(channel, method, frame, data: CollectedData):

    print(
        f"Consumer 2 received data.  Now processing data with counter {data.counter} ..."
    )

    # Simulate processing data
    time.sleep(3)

    # Finally acknowledge using standard pika
    channel.basic_ack(method.delivery_tag)

    print(f"Consumer 2 done.")
