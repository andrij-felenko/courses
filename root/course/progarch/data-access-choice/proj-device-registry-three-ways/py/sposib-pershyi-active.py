import django
from django.conf import settings

settings.configure(
    INSTALLED_APPS=["reg"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3",
                           "NAME": ":memory:"}},   # та сама вбудована SQLite
)
django.setup()

# reg/models.py
from django.db import models

class Device(models.Model):
    type      = models.CharField(max_length=32)
    room      = models.CharField(max_length=64)
    state     = models.CharField(max_length=32, default="unknown")
    last_seen = models.IntegerField(null=True)        # секунди епохи
    class Meta:
        app_label = "reg"

    def is_silent(self, now: int, threshold: int) -> bool:
        return self.last_seen is None or now - self.last_seen > threshold
