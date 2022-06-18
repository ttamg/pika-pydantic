# Sample project

An example using Pika-Pydantic in a project structure where we separate out the Queues, Models and Channel.
We can then have multiple Producers and Consumers using the same boilerplate setup.

In this example we have the following elements:

- A Producer that sends messages (sends a random message every 10 seconds in this example) to the MESSAGE queue
- A Consumer of the MESSAGE queue that prints that message and then simulates collecting some data from an API and then passes that to another job as a Producer on the DATA queue
- A Consumer of the DATA queue that takes the collected data and simulates processing it.

In terms of structure:

- `models.py` contains our pydantic type models for the data to be passed to the message queues
- `queues.py` contains our Enum type definitions of the valid queues and the corresponding data models on each queue.
- `channel.py` contains our boilerplate setup of channel that all Consumers and Publishers will use.
- `run.py` is a script that starts up the different Producers and Consumers

You can run this from the project command line using

    python -m examples.sample_project.run
