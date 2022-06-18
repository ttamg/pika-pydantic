import pika_pydantic

from . import models


class Queues(pika_pydantic.Queues):

    MESSAGE = models.Message
    PROCESS_DATA = models.CollectedData
