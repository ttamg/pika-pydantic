from typing import List

from aenum import Enum, NoAlias

from pika_pydantic.model import BaseModel


class Queues(Enum):
    """Defines the queues and the data model valid on each queue."""

    _settings_ = NoAlias

    @classmethod
    def all_queues(cls) -> List[str]:
        """Returns a list of all queue names in the Enum"""
        return [str(e.name) for e in cls]

    @classmethod
    def all_models(cls) -> List[str]:
        """Returns a list of all models in the Enum"""
        return [e.value for e in cls]


class ExampleQueues(Queues):
    """
    An example of queues.

    The enum name also doubles up as the RabbitMQ queue name as a string
    The value of the enum is the data model to use for validating all Producers and Consumers on this queue
    """

    FIRST = BaseModel
    SECOND = BaseModel
