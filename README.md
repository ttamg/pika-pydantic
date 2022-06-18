# Pika-Pydantic

An opinionated Python implementation of the Producer-Consumer Pattern using RabbitMQ on top of `pika` and `pydantic`.

# Introduction

This `pika_pydantic` library is a thin wrapper on top of the `pika` and `pydantic` libraries that makes it quick and easy to create **Producer-Consumer** workers that interface with a **RabbitMQ** message queue. For more information of why this library was created, see the Backstory section below in the documentation.

I was inspired in many ways by what Sebastian created with `FastAPI` by building on top of good existing libraries. `pika_pydantic` attempts to follow that method in its own much simpler way for the **asynchronous Producer-Consumer pattern using RabbitMQ**.

If you are creating a long chain of Producers and Consumers then the `pika_pydantic` library can save quite a lot of boilerplate code and potential errors.

# Installation

To install the `pika_pydantic` package using pip

    pip install pika-pydantic

Or using poetry

    poetry add pika-pydantic

# Dependencies - requires RabbitMQ

In addition you need to have a **RabbitMQ** instance up and running that can receive and route the messages.

If you have some familiarity with Docker, the easiest method is to spin up a docker container running RabbitMQ and use that as your message service. The `docker-compose-rabbit.yml` provides a simple `docker-compose` configuration script for this.

Alternatively, you can install RabbitMQ natively on your development machine or server, or link to a hosted RabbitMQ instance. More details on RabbitMQ installation can be found on [the official RabbitMQ documentation](https://www.rabbitmq.com/#getstarted)

# Quickstart

This simple example creates a simple message Producer-Consumer that passes around a message object.

## Create the pika connection

First we create a pika connection to the RabbitMQ system

```python
import pika

parameters = pika.URLParameters("amqp://guest:guest@localhost:5672/")
connection = pika.BlockingConnection(parameters)
```

This creates a normal `pika` blocking connection.  
The [`pika` documentation can be found here](https://pika.readthedocs.io/en/stable/)

## Pika-pydantic Channel vs pika Channel

Now we deviate from the standard `pika` method. Instead of using `connection.channel()` or similar to create a `pika.BlockingChannel` we use the `pika_pydantic.BlockingChannel` object instead. This object also initialises queues and adds various other useful methods on top of the standard `pika.BlockingChannel` object.

But before we do that we need to define the data validation and the queues that will constrain and validate our Producers and Consumers.

## Defining data models

We want to pass around a message data object that has a title, and text.
This data model is defined using the `pika_pydantic.BaseModel` which is a wrapper around the standard `pydantic.BaseModel`

```python
import pika_pydantic

class MyMessage(pika_pydantic.BaseModel):
    """A message"""
    title: str
    text: str
```

> `pika_pydantic.BaseModel` objects are pydantic.BaseModel objects with some additional elements for encoding and decoding the objects for RabbitMQ. See the [pydantic documentation](https://pydantic-docs.helpmanual.io/usage/models/) for more details.

## Defining queues

We also define the single message queue we will use in this example by definding an `pika_pydantic.Queues` enum in which each element defines both the rabbitMQ queue name to use, AND the data model to validate the data against.

```python
class MyQueues(pika_pydantic.Queues):
    MESSAGE = ("message_queue_name", MyMessage)
```

This object is the master that defines the valid queues and the corresponding data that all Producers and Consumers must use. Add more elements to this enum as you add queues and data models.

> `pika_pydantic.Queues` objects are a Python `enum.Enum` class but we define the values as a two-tuple. The first element of the tuple is the string name of the queue to be used in RabbitMQ. The second element of the tuple is the `pika_pydantic.BaseModel` data model object that all Producers and Consumers on this queue need to use.

## Initialise the Channel

Now we can initialise the channel and we pass it the `pika.connection` and the `pika_pydantic.Queues` enum we just defined.

```python
channel = pika_pydantic.BlockingChannel(connection=connection, queues=MyQueues)
```

> `pika_pydantic.BlockingChannel` is a `pika.BlockingChannel` object with some additional methods attached that allow simpler creation of Consumers (`smart_consume()`) and Producers (`smart_publish()`)

This object declares all the queues, and validates the message data on each queue and does the necessary encoding and decoding of the data for Consumers and Producers.

## Create a Consumer

To create a new Consumer for this message queue we use the new `channel.smart_consume(queue, callback)` method. This validates the inputs and does the decoding needed for that particular queue. We define a callback as in pika and add the consumer to the channel.

```python
def callback(channel, method, frame, data: MyMessage):
    print(f"Received message with title ({data.title}) and text ({data.text}).")

channel.smart_consume(queue=MyQueues.MESSAGE, callback=callback, auto_ack=True)
```

## Create a Producer

To create a Producer we use the new `channel.smart_publish(queue, data)` method. This takes the data object and does all the validation and encoding needed to pass it to the RabbitMQ queue.

```python
message = MyMessage(title="Important", text="Remember to feed the dog")
channel.smart_publish(queue=MyQueues.MESSAGE, data=message)
```

## Start it running

As with standard pika, the channel can start polling so that the defined Consumers start listening for messages on their queue.

```python
channel.start_consuming()
```

Or to not block the thread and process the messages currently in the queue we can use

```python
connection.process_data_events(time_limit=None)
```

# Other examples

The `examples` folder provides further examples and a suggested project folder structure that reuses the `pika_pydantic` elements across multiple Consumers and Producers.

# The backstory

## Asynchronous messaging

Good code structure generally separates concerns (jobs) between different modules. Microservices takes this one step further and separates jobs into different deployable systems that interact with each other.

These different systems are interfaced through various APIs, usually called from one system to another in realtime.

But some jobs are long lasting or resource hungry and this is where we can use asynchronous interfaces between the different systems.

There is a lot of interest currently in Kafka as a system for managing these asynchronous jobs. But for most projects a simpler message queue such as RabbitMQ will do the job. It provides a way to pass data and a job onto another system, and that other system will pick up the job when it has resources to do so.

## The Producer-Consumer pattern

For many purposes a system does some work and prepares some data. It then passes this on as a job for the next system element to work on when it has resources available. This is the **Producer-Consumer Pattern**.

In a bit more detail

- A Producer completes some job, often resulting in some data artifact to be passed to the next stage.
- The Producer publishes this data to a message queue
- The next job is a Consumer of this message queue. When it has resources available, it picks up the message and the published data and then does it work.
- This Consumer may itself also be a Producer publishing it's data to a different message queue for the next Consumer in the chain to take forward.

## RabbitMQ and the Python `pika` library

In the Python world there are good libraries for this, most notably is the `pika` library that interfaces with a RabbitMQ message queue. `pika` is relatively simple and very flexible.

But for my needs I wanted to use stricter software development principles and the flexibility of `pika` too flexible. Specifically:

- My system has many Consumers and many Publishers. I wanted to be able to define the `pika` boilerplate code to set up the connection, the queues and the channel in one central place for all the different jobs.
- I also wanted to restrict my Consumers and Publishers to only valid queues, so to do this I wanted to define the valid queues in an Enum to reduce strange bugs.
- I wanted to ensure that each Producer sending data sends the data in the right format and each Consumer picks up the data and validates to the same format. For this the `pydantic` library is very helpful to constrain the Producer and Consumer data to be passed. This is how the `fastapi` library ensures data being passed around that API is validated and structured correctly. I wanted to use this pattern.

## Contributing

If you find this useful, consider adding a star and contributing.

Currently this only uses the `pika.BlockingChannel` implementation.

## Tests

When running tests, a RabbitMQ instance needs to be up and running on your machine as the tests do live tests using that RabbitMQ.

If using docker, you can spin up a RabbitMQ instance for testing using

    docker-compose -f docker-compose-rabbit.yml up

The environment variable `RABBIT_URL` can be overwritten to point to your test RabbitMQ instance.

Then run tests use **pytest**

    pytest
