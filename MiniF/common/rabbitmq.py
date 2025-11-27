import pika
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def publish_to_rabbitmq(exchange, routing_key, body):
    connection = None
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
        )
        channel = connection.channel()
        
        channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)
        
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent
            )
        )
        logger.info(f"Published {routing_key} event to {exchange}")
        
    except Exception as e:
        logger.error(f"Failed to publish RabbitMQ message: {e}")
    finally:
        if connection and not connection.is_closed:
            connection.close()
