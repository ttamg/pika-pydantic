import pika_pydantic
from pika_pydantic.queues import ExampleQueues


def test_queues_all_method():

    assert ExampleQueues.SECOND.name == "SECOND"
    assert ExampleQueues.SECOND.value == pika_pydantic.BaseModel

    assert ExampleQueues.all_queues() == ["FIRST", "SECOND"]
    assert ExampleQueues.all_models() == [
        pika_pydantic.BaseModel,
        pika_pydantic.BaseModel,
    ]
