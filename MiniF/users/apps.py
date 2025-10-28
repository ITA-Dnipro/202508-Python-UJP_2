from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class UsersConfig(AppConfig):
    """Configuration class for the users app.
    Loads and registers signals on startup.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        """Import user-related signal handlers when the app is ready."""
        try:
            import users.signals  # pylint: disable=import-outside-toplevel
            logger.debug("Users app ready: signals successfully imported.")
        except ImportError as e:
            logger.warning("Failed to import users.signals: %s", e)