import pika_pydantic
import pika

"""
This sets up a simple messaging Producer and Consumer with a defined message object.

This requires manual acknowledgement - see pika documentation for more details
"""

# Our data model for data to pass to the queue
class MyMessage(pika_pydantic.BaseModel):
    title: str
    text: str


# Our Queue definitions
class MyQueues(pika_pydantic.Queues):
    MESSAGE = MyMessage


# Initialise the pika blocking connection as for standard Pika
parameters = pika.URLParameters("amqp://guest:guest@localhost:5672/")
connection = pika.BlockingConnection(parameters)


# Initialise the pika-pydantic BlockingChannel
channel = pika_pydantic.BlockingChannel(connection=connection, queues=MyQueues)


# Define our message Consumer
def callback(channel, method, frame, data: MyMessage):
    # Note that the data for this callback has already been decoded, validated
    # and converted into pydantic BaseModel object
    print(f"I received a message with title ({data.title}) and text ({data.text}).")
    # Acknowledge using standard pika
    channel.basic_ack(method.delivery_tag)


channel.listen(queue=MyQueues.MESSAGE, callback=callback, auto_ack=False)
