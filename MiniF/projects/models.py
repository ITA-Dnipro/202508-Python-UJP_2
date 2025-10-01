from django.db import models
from django.utils import timezone

class StartupProject(models.Model):
    """
    Startup project model.

    Notes:
    - Added default=0 to the likes field.
    """
    startup_profile_id = models.ForeignKey('profiles.StartupProfile', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    likes = models.IntegerField(default=0)
    description = models.TextField()
    status = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return self.title
