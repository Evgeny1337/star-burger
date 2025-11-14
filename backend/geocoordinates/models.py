from django.db import models
import datetime

class PlaceCoordinates(models.Model):
    address = models.CharField(
        'Адрес места',
        max_length=255,
        unique=True,
        db_index=True
    )
    lat = models.FloatField('Широта')
    lon = models.FloatField('Долгота')
    updated_at = models.DateTimeField(
        'Дата обновления координат',
        auto_now=True
    )

    class Meta:
        verbose_name = 'координаты места'
        verbose_name_plural = 'координаты мест'

    def __str__(self):
        return f'{self.address} ({self.lat}, {self.lon})'

    def is_expired(self):
        return (datetime.datetime.now() - self.updated_at.replace(tzinfo=None)) > datetime.timedelta(days=30)
