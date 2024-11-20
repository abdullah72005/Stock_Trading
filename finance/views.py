from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


from .models import Client, Owned, Transaction
from finance.helpers import lookup, usd

# Create your views here.
@login_required
def index_view(request):
    
    # render with balance and owned stocks
    # return render(request, "index.html", {})
    return render('<h1>Hello World home</h1>')



@login_required
def buy_view():

    return HttpResponse('<h1>Hello World buy</h1>')


@login_required
def history_view():
    """Show history of transactions"""

    # pass data to template and render history html page
    return HttpResponse('<h1>Hello World history</h1>')



def login_view(request):
    """Log user in"""

    return HttpResponse('<h1>Hello World login</h1>')


def logout_view(request):
    """Log user out"""

    # Forget any user_id
    request.session.flush()

    # Redirect user to login form
    return redirect("login/")

#this take from the quoteForm in forms.py
#read the else statment before the if
@login_required
def quote_view(request):
    if request.method == "POST":
        #takes the form after it's been filled
        stock_name = request.POST.get('symbol')
        #calls the api and returns the price and name if found
        result = lookup(stock_name)
        #if not found send the user a letter
        if not result:
            return render('<h1>stock not found</h1>')
        context = {
            'result' : result
        }
        # if found it renders the new page which tells the price
        return render(request, "quoted.html", context)
    else:
        return render(request, "quote.html", {})



def register_view(request):

    return HttpResponse('<h1>Hello World register</h1>')



@login_required
def sell_view(request):
    """Sell shares of stock"""
    username = request.user.username
    user = Client.objects.get(username = username)
    balance = user.cash
    stocks = Owned.objects.filter(Username = user.id)
    if request.method == "POST":
        symbol = request.POST.get('symbol')
        if not symbol:
            return HttpResponse('<h1>select a symbol</h1>')
        try:
            # Use get_object_or_404 to efficiently find the stock by symbol
            stock = get_object_or_404(stocks, symbol=symbol) 
        except:  # Handle the case where the stock is not found
            return False
        stock = Owned.objects.get(symbol = symbol,Username = user.id)
        shares = request.POST.get('shares')
        if int(shares) > int(stock.shares):
            return HttpResponse('<h1>not enough shares/h1>')
        lookupResult = lookup(symbol)
        new_cash = float(user.cash) + ((lookupResult["price"]) * float(shares))
        user.cash = new_cash
        user.save()
        stock.shares -= int(shares)
        if stock.shares == 0:
            stock.delete()
        else:
            stock.save()
        Transaction.objects.create(purchase_type = 'sell',price_when_bought = lookupResult["price"], shares = shares, symbol = lookupResult["symbol"], Username = user)
        return render(request, "index.html", {})


        
    else:

        context = {
            'stocks' : stocks,
            'balance' : balance,
        }
        return render(request, "sell.html", context)



@login_required
def balance_view():

    return HttpResponse('<h1>Hello World balance</h1>')


