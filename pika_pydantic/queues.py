import enum
from typing import List

from pika_pydantic.model import BaseModel


class Queues(enum.Enum):
    """A wrapper around a simple string Enum that returns the value (name of the queue) as its string representation"""

    @classmethod
    def all_queues(cls) -> List[str]:
        """Returns a list of all queue names in the Enum"""
        return [e.value[0] for e in cls]

    @classmethod
    def all_models(cls) -> List[str]:
        """Returns a list of all models in the Enum"""
        return [e.value[1] for e in cls]


class ExampleQueues(Queues):
    """
    An example of queues.

    The first element in each tuple is the string name of the queue to be used in RabbitMQ
    The second element in each tuple is the data model to be used for validation by all Consumers and Producers on that queue.
    """

    FIRST = ("first", BaseModel)
    SECOND = ("second", BaseModel)
