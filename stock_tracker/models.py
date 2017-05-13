# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

# Create your models here.

class Company(models.Model):
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    exchange = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    historic_collected = models.BooleanField(default=False)

    def __str__(self):
        return "%s - %s (%s)" % (self.symbol, self.name, self.exchange)


class Stock(models.Model):
    company = models.ForeignKey('Company')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.IntegerField()
    date = models.DateField(default=timezone.now, db_index=True)

    def __str__(self):
        return '%s - %s - %s - %s' % (self.company.name, self.price, self.volume, self.date)