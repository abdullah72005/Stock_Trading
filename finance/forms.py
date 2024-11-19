from django import forms
from .models import Client, Owned, Transaction
#a form with a single input that a asks for a name of a stock and returns it's price
class quoteForm(forms.Form):
    stock_name = forms.CharField(label='Stock Name') 
    def clean_stock_name(self):
        stock_name = self.cleaned_data['stock_name']
        # Add your validation logic here (e.g., check for valid characters)
        return stock_name 