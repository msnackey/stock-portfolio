from django.db import models
from django.urls import reverse
import yfinance as yf


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=256, unique=True)
    target = models.DecimalField(max_digits=3, decimal_places=0)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main_app:invest')

    def calc_cat_value(self):
        value = 0
        stocks = self.stocks.all()
        for stock in stocks:
            value = value + stock.calc_value()
        return value

    def perc(self):
        cat_value = self.calc_cat_value()
        sum = 0
        for product in Stock.objects.all():
            value = product.shares * product.price
            sum = sum + value

        if sum == 0:
            return 0

        return cat_value/sum*100

    def perc_delta(self):
        return self.perc() - self.target


class StockManager(models.Manager):
    def sum_all(self):
        sum = 0
        for stock in Stock.objects.all():
            value = stock.shares * stock.price
            sum = sum + value
        return sum


class Stock(models.Model):
    product = models.CharField(max_length=256, null=True)
    ticker = models.CharField(max_length=7)
    currency = models.CharField(max_length=3, null=True)
    exchange = models.CharField(max_length=3, null=True)
    category = models.ForeignKey(Category, related_name='stocks', on_delete=models.CASCADE)
    sri = models.BooleanField()
    shares = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=19, decimal_places=10, default=0)
    invest = models.BooleanField()
    value = models.DecimalField(max_digits=19, decimal_places=10, default=0)
    prev_price = models.DecimalField(max_digits=19, decimal_places=10, null=True)
    price_change_perc = models.DecimalField(max_digits=19, decimal_places=10, default=0)
    value_change = models.DecimalField(max_digits=19, decimal_places=10, default=0)

    objects = StockManager()

    def __str__(self):
        return self.ticker

    def get_absolute_url(self):
        return reverse('main_app:list')

    def calc_value(self):
        value = self.shares * self.price
        return value

    def get_stock_data(self):
        info = yf.Ticker(self.ticker).info
        return info
