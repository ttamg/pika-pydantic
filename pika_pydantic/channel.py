from __future__ import annotations

from typing import Callable

import pika

from pika_pydantic.exceptions import PikaPydanticException
from pika_pydantic.model import BaseModel
from pika_pydantic.queues import Queues


class BlockingChannel(pika.adapters.blocking_connection.BlockingChannel):
    """
    An extension of the pika.BlockingChannel object that adds additional methods for
    creating consumers and producers with defined queues and stronger validation.

    Additional methods are:

    - smart_consume() - starts a new Consumer
    - smart_publish() - sends a message to a queue as a Producer

    These are opinionated implementations that perform validation

    When initialising the pika_pydantic.BlockingChannel you also need to pass an pika_pydantic.Queues object which
    will ensure that those queues are declared and created on start up, and also validate that
    only those queues and the right data structure for the messages are used.
    """

    def __init__(
        self, connection: pika.BlockingConnection, queues: Queues, **kwargs
    ) -> BlockingChannel:

        # Validation
        if not isinstance(connection, pika.BlockingConnection):
            raise Exception(f"connection can only be a pika.BlockingConnection.")
        if not issubclass(queues, Queues):
            raise PikaPydanticException(f"queues must be a pika_pydantic.Queues queue.")

        # Create channel
        pika_blockingchannel = connection.channel(**kwargs)
        self._pika_blockingchannel = pika_blockingchannel

        # Register this object as the proxy cookie for this channel
        channel_number = self.channel_number
        assert channel_number in connection._impl._channels.keys()
        channel_impl = connection._impl._channels[channel_number]
        channel_impl._set_cookie(self)

        # Set up queues
        self.queues = queues
        for queue in self.queues.all_queues():
            self.queue_declare(queue=queue, durable=True)

    def __getattr__(self, attr):
        """Map pika.BlockingChannel attributes to the pika_pydantic.BlockingChannel attributes"""
        return getattr(self._pika_blockingchannel, attr)

    def _dispatch_events(self):
        """Called by BlockingConnection to dispatch pending events.
        `BlockingChannel` schedules this callback via
        `BlockingConnection._request_channel_dispatch`
        """
        while self._pending_events:
            evt = self._pending_events.popleft()

            if (
                type(evt) is pika.adapters.blocking_connection._ConsumerDeliveryEvt
            ):  # pylint: disable=C0123
                consumer_info = self._consumer_infos[evt.method.consumer_tag]
                consumer_info.on_message_callback(
                    self, evt.method, evt.properties, evt.body
                )

            elif (
                type(evt) is pika.adapters.blocking_connection._ConsumerCancellationEvt
            ):  # pylint: disable=C0123
                del self._consumer_infos[evt.method_frame.method.consumer_tag]

                self._impl.callbacks.process(
                    self.channel_number,
                    self._CONSUMER_CANCELLED_CB_KEY,
                    self,
                    evt.method_frame,
                )
            else:
                evt.dispatch()

    def smart_consume(self, queue: Queues, callback: Callable, **kwargs):
        """
        Additional helper method on the pika.channel object to set up a consumer on the
        queue (pika_pydantic.Queue) that will parse the data using the relevant pika_pydantic.BaseModel and
        pass that to the callback.

        The callback receives the following parameters(channel, method, header, data).
        Note that a difference in this callback is that this consume function already validates
        and decodes the body data into relevant BaseModel in the data parameter.

        Additional kwargs for the pika.basic_consume() method can be passed if desired.

        Returns the pika.BlockingChannel consumer_tag
        """

        # Validate inputs
        if queue not in self.queues:
            raise PikaPydanticException(f"Queue not recognised.")
        if not callable(callback):
            raise PikaPydanticException(
                f"Callback must be a callable with parameters (channel, method, header, data)."
            )

        queue_name = queue.value[0]
        model = queue.value[1]

        def validated_callback(channel, method, header, body):
            """Callback wrapped to first decode and validate the body data."""
            data = model.decode(body)
            return callback(channel, method, header, data)

        return self.basic_consume(
            queue=queue_name, on_message_callback=validated_callback, **kwargs
        )

    def smart_publish(self, queue: Queues, data: BaseModel, exchange="", **kwargs):
        """
        Additional helper method on the pika.channel object that publishes the data (pika_pydantic.BaseModel)
        to the queue (pika_pydantic.Queue).

        This is a wrapper around the standard pika.basic_publish() method that includes
        validation of the data, the queue and encodes the data.

        Additional kwargs for the pika.basic_publish() method can be passed if desired
        """

        # Validate inputs
        if queue not in self.queues:
            raise PikaPydanticException(f"Queue not recognised.")
        if not isinstance(data, queue.value[1]):
            raise PikaPydanticException(
                f"Data to publish to this queue must be a {queue.value[1]} object."
            )

        queue_name = queue.value[0]

        self.basic_publish(
            exchange=exchange, routing_key=queue_name, body=data.encode(), **kwargs
        )
