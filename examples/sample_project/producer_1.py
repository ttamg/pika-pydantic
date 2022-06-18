import random

from .channel import open_channel
from .models import Message
from .queues import Queues

"""
Simulates producing messages every 10 seconds 
"""


def producer_1():
    print("Starting up producer 1.")

    channel = open_channel()

    while True:
        channel._connection.sleep(10)

        print("Producer 1 generating a message now.")

        message = Message(title="Important", text=f"I rolled a {random.randint(1,7)}")
        channel.smart_publish(Queues.MESSAGE, message)

        print("Producer 1 done.")
