from django.core.management.base import BaseCommand
from notifications.consumers.rabbitmq_listener import start_notification_consumer

class Command(BaseCommand):
    help = "Starts RabbitMQ notification consumer"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting Notification Consumer...")
        start_notification_consumer()
