import json
import pika
import logging
from django.db import transaction
from notifications.models import Notification, NotificationType

logger = logging.getLogger(__name__)

def start_notification_consumer():
    logger.info("Starting RabbitMQ Notification Consumer...")

    connection_params = pika.ConnectionParameters(
        host="rabbitmq",
        port=5672,
        credentials=pika.PlainCredentials("guest", "guest")
    )

    try:
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        channel.queue_declare(queue="notifications")
        logger.info("Connected to RabbitMQ (queue: notifications)")
    except Exception as e:
        logger.error(f"annot connect to RabbitMQ: {e}")
        return

    def callback(ch, method, properties, body):
        logger.info("Incoming message from RabbitMQ")

        try:
            message = json.loads(body)
            logger.info(f"Parsed message JSON: {message}")

            notif_type_name = message.get("type")
            user_id = message.get("user_id")
            project_id = message.get("project_id")
            extra = message.get("extra", {})

            if not notif_type_name:
                logger.warning("Missing notification 'type'. Skipping.")
                return

            # UPSERT NotificationType
            notif_type, _ = NotificationType.objects.get_or_create(name=notif_type_name)

            # Store notification
            with transaction.atomic():
                notif = Notification.objects.create(
                    user_id=user_id,
                    project_id=project_id,
                    type=notif_type,
                    extra_data=extra,
                )

            logger.info(f"Notification stored successfully (id={notif.id})")

        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=True)

    channel.basic_consume(
        queue="notifications", on_message_callback=callback, auto_ack=True
    )

    logger.info("Notification consumer is now listening...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Notification consumer stopped manually")
    except Exception as e:
        logger.error(f"Consumer crashed: {e}", exc_info=True)
