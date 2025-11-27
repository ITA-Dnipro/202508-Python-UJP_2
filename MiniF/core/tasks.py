from celery import shared_task
from celery.utils.log import get_task_logger
from common.rabbitmq import publish_to_rabbitmq

logger = get_task_logger(__name__)

@shared_task
def publish_event_task(exchange, routing_key, body):
    logger.info(f"Task publish_event_task started for {routing_key}")
    try:
        publish_to_rabbitmq(exchange, routing_key, body)
        logger.info(f"Task publish_event_task completed for {routing_key}")
    except Exception as e:
        logger.error(f"Task publish_event_task failed: {e}")

