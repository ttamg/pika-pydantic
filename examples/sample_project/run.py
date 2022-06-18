import time
from threading import Thread

from .channel import open_channel
from .consumer_1 import consumer_1
from .consumer_2 import consumer_2
from .producer_1 import producer_1
from .queues import Queues

"""
Start up the consumers in one thread and the producer in another
"""

# As pika is not threadsafe, producer runs on a separate channel / connection
producer_thread = Thread(target=producer_1)
producer_thread.start()


print("Starting up consumers.")
channel = open_channel()

channel.smart_consume(queue=Queues.MESSAGE, callback=consumer_1, auto_ack=False)
channel.smart_consume(queue=Queues.PROCESS_DATA, callback=consumer_2, auto_ack=False)

channel.start_consuming()
