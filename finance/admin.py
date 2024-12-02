from django.contrib import admin

from .models import Client, Owned, Transaction, Portfolio

# Register your models here.
admin.site.register(Client)
admin.site.register(Owned)
admin.site.register(Transaction)
admin.site.register(Portfolio)