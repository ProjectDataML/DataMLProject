from django.db import models

class Calendar(models.Model):
    listing_id = models.IntegerField()
    date = models.DateField()
    available = models.CharField(max_length=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    adjusted_price = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_nights = models.IntegerField()
    maximum_nights = models.IntegerField()
