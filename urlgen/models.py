from django.db import models
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class URLdb(models.Model):
    short_url_key = models.CharField(max_length=256, null=False, unique=True)
    hits = models.IntegerField(default=1)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)  # TTL of 7 days
        super().save(*args, **kwargs)