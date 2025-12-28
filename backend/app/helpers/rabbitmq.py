"""
RabbitMQ helper for direct message queue interaction.

Use this for non-Celery use cases:
- Custom event publishing
- Real-time notifications
- Microservice communication
- Message queuing patterns
"""

import asyncio
import json
from typing import Any, Callable, Dict, Optional

try:
    import aio_pika
    from aio_pika import Message, ExchangeType
    from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractQueue
    AIOPIKA_AVAILABLE = True
except ImportError:
    AIOPIKA_AVAILABLE = False
    # Define placeholder types when aio_pika is not available
    AbstractQueue = Any  # type: ignore
    AbstractChannel = Any  # type: ignore
    AbstractConnection = Any  # type: ignore

from app.config.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RabbitMQHelper:
    """RabbitMQ async helper for direct queue operations."""

    def __init__(self):
        self._connection: Optional[AbstractConnection] = None
        self._channel: Optional[AbstractChannel] = None
        self.enabled = settings.enable_rabbitmq and AIOPIKA_AVAILABLE

    async def initialize(self):
        """Initialize RabbitMQ connection."""
        if not self.enabled:
            logger.warning("RabbitMQ is not enabled or aio-pika not installed")
            return

        try:
            # Parse RabbitMQ URL
            broker_url = settings.rabbitmq_url or "amqp://guest:guest@rabbitmq:5672/"

            # Create connection
            self._connection = await aio_pika.connect_robust(
                broker_url,
                loop=asyncio.get_event_loop(),
            )

            # Create channel
            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=10)

            logger.info("RabbitMQ connection established")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self.enabled = False

    async def close(self):
        """Close RabbitMQ connection."""
        if self._channel:
            await self._channel.close()
        if self._connection:
            await self._connection.close()
        logger.info("RabbitMQ connection closed")

    async def publish_message(
        self,
        exchange: str,
        routing_key: str,
        message: Dict[str, Any],
        exchange_type: str = "topic",
        durable: bool = True,
    ):
        """
        Publish message to exchange.

        Args:
            exchange: Exchange name
            routing_key: Routing key for message
            message: Message payload (will be JSON serialized)
            exchange_type: Exchange type (topic, direct, fanout, headers)
            durable: Whether message should survive broker restart
        """
        if not self.enabled or not self._channel:
            raise RuntimeError("RabbitMQ is not initialized")

        # Declare exchange
        ex = await self._channel.declare_exchange(
            exchange,
            type=ExchangeType(exchange_type),
            durable=durable,
        )

        # Create message
        body = json.dumps(message).encode()
        msg = Message(
            body,
            delivery_mode=2 if durable else 1,  # Persistent or transient
            content_type="application/json",
        )

        # Publish
        await ex.publish(msg, routing_key=routing_key)
        logger.debug(f"Published message to {exchange}/{routing_key}")

    async def consume_messages(
        self,
        queue_name: str,
        callback: Callable,
        exchange: Optional[str] = None,
        routing_key: Optional[str] = None,
        exchange_type: str = "topic",
        durable: bool = True,
    ):
        """
        Consume messages from queue.

        Args:
            queue_name: Queue name
            callback: Async function to handle messages
            exchange: Optional exchange to bind to
            routing_key: Optional routing key for binding
            exchange_type: Exchange type
            durable: Whether queue should survive broker restart
        """
        if not self.enabled or not self._channel:
            raise RuntimeError("RabbitMQ is not initialized")

        # Declare queue
        queue = await self._channel.declare_queue(
            queue_name,
            durable=durable,
        )

        # Bind to exchange if specified
        if exchange and routing_key:
            ex = await self._channel.declare_exchange(
                exchange,
                type=ExchangeType(exchange_type),
                durable=durable,
            )
            await queue.bind(ex, routing_key=routing_key)

        # Consume messages
        async def process_message(message):
            async with message.process():
                try:
                    body = json.loads(message.body.decode())
                    await callback(body)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        await queue.consume(process_message)
        logger.info(f"Started consuming from queue: {queue_name}")

    async def create_queue(
        self,
        queue_name: str,
        durable: bool = True,
        auto_delete: bool = False,
        exclusive: bool = False,
    ) -> AbstractQueue:
        """
        Create/declare a queue.

        Args:
            queue_name: Queue name
            durable: Queue survives broker restart
            auto_delete: Queue deleted when last consumer unsubscribes
            exclusive: Queue used by only one connection

        Returns:
            Queue object
        """
        if not self.enabled or not self._channel:
            raise RuntimeError("RabbitMQ is not initialized")

        queue = await self._channel.declare_queue(
            queue_name,
            durable=durable,
            auto_delete=auto_delete,
            exclusive=exclusive,
        )

        logger.info(f"Created queue: {queue_name}")
        return queue

    async def create_exchange(
        self,
        exchange_name: str,
        exchange_type: str = "topic",
        durable: bool = True,
    ):
        """
        Create/declare an exchange.

        Args:
            exchange_name: Exchange name
            exchange_type: Exchange type (topic, direct, fanout, headers)
            durable: Exchange survives broker restart
        """
        if not self.enabled or not self._channel:
            raise RuntimeError("RabbitMQ is not initialized")

        await self._channel.declare_exchange(
            exchange_name,
            type=ExchangeType(exchange_type),
            durable=durable,
        )

        logger.info(f"Created exchange: {exchange_name} ({exchange_type})")

    async def purge_queue(self, queue_name: str):
        """Delete all messages from queue."""
        if not self.enabled or not self._channel:
            raise RuntimeError("RabbitMQ is not initialized")

        queue = await self._channel.get_queue(queue_name)
        await queue.purge()
        logger.info(f"Purged queue: {queue_name}")

    async def delete_queue(self, queue_name: str):
        """Delete a queue."""
        if not self.enabled or not self._channel:
            raise RuntimeError("RabbitMQ is not initialized")

        queue = await self._channel.get_queue(queue_name)
        await queue.delete()
        logger.info(f"Deleted queue: {queue_name}")


# Global instance
rabbitmq_helper = RabbitMQHelper()
