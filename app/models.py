from django.db import models

# Create your models here.


class StockData(models.Model):
    date = models.DateField(primary_key=True)
    close_price = models.FloatField()
