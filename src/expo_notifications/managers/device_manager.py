from django.db import models


class DeviceQueryset(models.QuerySet):
    @property
    def active(self) -> "DeviceQueryset":
        return self.filter(is_active=True)


class DeviceManager(models.Manager):
    def get_queryset(self) -> "DeviceQueryset":
        return DeviceQueryset(self.model, using=self._db)

    @property
    def active(self) -> "DeviceQueryset":
        return self.get_queryset().active
