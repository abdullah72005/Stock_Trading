from django.db import models
from django.utils.timezone import now
from decimal import Decimal
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Client(AbstractUser):
    cash        = models.DecimalField(blank=False, null=False, default=10000.00, max_digits=13, decimal_places=2)

    def get_cash(self):
        return self.cash

    def set_cash(self, amount):
        self.cash = Decimal(amount)
        self.save()

    def __str__(self):
        return self.username


class Owned(models.Model):
    symbol      = models.CharField(max_length=5, blank=False, null=False)
    shares      = models.IntegerField(blank=False, null=False)
    stock_price = models.DecimalField(blank=False, null=False, decimal_places=2, max_digits=20)
    total       = models.DecimalField(blank=False, null=False, max_digits=20, decimal_places=2,)
    Username    = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="owned_stocks")

    def save(self, *args, **kwargs):
        self.total = Decimal(self.shares) * Decimal(self.stock_price)
        super().save(*args, **kwargs)

    def __str__(self):
         return f"{self.Username} owns {self.shares} shares of {self.symbol}"
    

class Transaction(models.Model):
    purchase_type = models.CharField(max_length=5, blank=False, null=False)
    price_when_bought = models.DecimalField(blank=False, null=False, max_digits=20, decimal_places=2)
    shares      = models.IntegerField(blank=False, null=False)
    symbol      = models.CharField(max_length=5, blank=False, null=False)
    time        = models.DateTimeField(auto_now_add = False, blank=False, null=False)
    Username    = models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL, related_name="user_transactions")

    def save(self, *args, **kwargs):
        # Set the current time if not already set
        if not self.time:
            self.time = now()

        # Call the parent save method
        super().save(*args, **kwargs)

    def __str__(self):
         return f"{self.purchase_type.capitalize()} {self.shares} shares of {self.symbol} by {self.Username}"
    