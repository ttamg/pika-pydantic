import pika_pydantic

from . import models


class Queues(pika_pydantic.Queues):

    MESSAGE = ("messages", models.Message)
    PROCESS_DATA = ("process_it", models.CollectedData)
