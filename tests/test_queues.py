import pika_pydantic
from pika_pydantic.queues import ExampleQueues


def test_queues_all_method():

    assert ExampleQueues.all_queues() == ["first", "second"]
    assert ExampleQueues.all_models() == [
        pika_pydantic.BaseModel,
        pika_pydantic.BaseModel,
    ]

    assert ExampleQueues.SECOND.value[0] == "second"
    assert ExampleQueues.SECOND.value[1] == pika_pydantic.BaseModel
