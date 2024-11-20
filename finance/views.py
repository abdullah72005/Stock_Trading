from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist


from .models import Client, Owned, Transaction
from finance.helpers import lookup, usd
from .forms import quoteForm

# Create your views here.
@login_required
def index_view(request):
    
    # render with balance and owned stocks
    # return render(request, "index.html", {})
    return HttpResponse('<h1>Hello World home</h1>')



# WHEN LOGIN IS IMPLEMENTED THE NEXT 2 LINES SHOULD BE UNCOMMENTED AND THE THIRD SHOULD BE DELETED
####################################################### @login_required
def buy_view(request):
    """Buy shares of stock"""
    
    # get user id
    ################################################### userid = request.sessions.get("user_id")
    userid = request.user.id

    # get client(custom user) object inorder to access balance and other data
    c = Client.objects.get(id = userid)

    # get users balance
    balance = c.cash

    # if method is POST
    if request.method == "POST":
        # get data from the form
        symbol = request.POST.get("symbol").upper()
        shares = request.POST.get("shares")
        ptype = "Buy"

        # get the stock price from the api
        lookupResult = lookup(symbol)

        # check input
        if not symbol:
            return HttpResponse("Please enter stock symbol")
        if not shares:
            return HttpResponse("please enter shares amount")
        if not shares.isnumeric():
            return HttpResponse("please enter whole number")
        if float(shares) <= 0:
            return HttpResponse("Invalid input")
        if not lookupResult:
            return HttpResponse("Invalid stock symbol")
        
        # see cost and check if user can afford it
        purchasePrice = float(lookupResult["price"]) * float(shares)
        stockPrice = lookupResult["price"]
        if purchasePrice > balance:
            return HttpResponse("You don't have enough balance")
        
        # add purchase to db
        trans = Transaction(purchase_type=ptype, price_when_bought=stockPrice, shares=shares, symbol=symbol, Username=c)
        trans.save()

        # update users balance
        c.cash = float(balance) - purchasePrice
        c.save()

        # update users wallet
        try:
            owned_record = Owned.objects.get(symbol=symbol, Username_id=userid)
            owned_id = owned_record.id  # Get the ID of the stock in the wallet
        except ObjectDoesNotExist:
            owned_id = None  # it is his first time purchasing this stock


        # if it is his first time purchasing this stock insert it to the db
        if not owned_id:
            newStock = Owned(symbol=symbol, shares=shares, stock_price=stockPrice, total=purchasePrice, Username=c)
            newStock.save()

        # if its not his first time then update his wallet
        else:
            oldShares = Owned.objects.get(symbol=symbol, Username_id=userid).shares
            newShares = int(oldShares) + int(shares)
            owned_record.shares = newShares
            owned_record.total = stockPrice * newShares
            owned_record.save()

        # redirect to main page
        return redirect("/")
    else:
        # render buy template
        return render(request, "buy.html", { "balance":usd(balance) })



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
        form = quoteForm(request.POST)
        #checks wether the form is vaild and then takes the input and puts inside stock_name
        if form.is_valid():
            form.clean
            stock_name = form.cleaned_data['stock_name']
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
        #create a new form
        form = quoteForm()
        #put the form as an object
        context = {
            'form' : form
        }
        #sends the form to the page
        return render(request, "quote.html", context)



def register_view(request):

    return HttpResponse('<h1>Hello World register</h1>')



@login_required
def sell_view():
    """Sell shares of stock"""

    return HttpResponse('<h1>Hello World sell</h1>')



@login_required
def balance_view():

    return HttpResponse('<h1>Hello World balance</h1>')


