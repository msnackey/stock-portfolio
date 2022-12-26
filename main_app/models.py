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
        """Calculates the total value of the stocks of this category."""
        value = 0
        stocks = self.stocks.all()
        for stock in stocks:
            value = value + stock.calc_value()
        return value

    def perc(self):
        """Calculates the percentage of the category value in relation to the total value."""
        # Get the category value
        cat_value = self.calc_cat_value()
        # Get the total stock value
        value_sum = StockManager.sum_all()
        # If the total stock value is 0, return 0 (otherwise you will get a division error)
        if value_sum == 0:
            return 0
        return cat_value/value_sum*100

    def perc_delta(self):
        """Calculates the delta of the current percentage and the target percentage of the category."""
        return self.perc() - self.target


class StockManager(models.Manager):
    @staticmethod
    def sum_all():
        """Calculates the total value of all stocks."""
        value_sum = 0
        for stock in Stock.objects.all():
            value = stock.shares * stock.price
            value_sum = value_sum + value
        return value_sum


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

    # Links the StockManager class so it inherits the custom methods
    objects = StockManager()

    def __str__(self):
        return self.ticker

    def get_absolute_url(self):
        return reverse('main_app:list')

    def calc_value(self):
        """Calculates the value of the stock."""
        value = self.shares * self.price
        return value

    def get_stock_data(self):
        """Gets the stock data with the yfinance package using the stock ticker."""
        info = yf.Ticker(self.ticker).info
        return info
