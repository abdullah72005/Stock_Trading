from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist


from .models import Client, Owned, Transaction
from finance.helpers import lookup, usd

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
    userid = request.user.id # delete this

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




# WHEN LOGIN IS IMPLEMENTED THE NEXT 2 LINES SHOULD BE UNCOMMENTED AND THE THIRD SHOULD BE DELETED
######################################@login_required
def history_view(request):
    """Show history of transactions"""

    ############################################################# userid = session["user_id"]
    userid = request.user.id # delete this


    # get client(custom user) object inorder to use as foreign key in transactions
    c = Client.objects.get(id = userid)

    # get all user transactions
    transactions = Transaction.objects.filter(Username=c)

    # pass data to template and render history html page
    return render(request, "history.html", {"transactions":transactions})



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
    #gets user id
    userid = request.user.id
    #gets current user from id
    user = Client.objects.get(id = userid)
    #gets the user's cash amount
    balance = user.cash
    #gets all the stocks the user have
    stocks = Owned.objects.filter(Username = user.id)
    if request.method == "POST":
        #gets the symbol choesn from the form
        symbol = request.POST.get('symbol')
        #checks if the user inputs a symbol
        if not symbol:
            return HttpResponse('<h1>select a symbol</h1>')
            #checks if the user owns this symbol
        try:
            stock = get_object_or_404(stocks, symbol=symbol) 
        except: # Handle the case where the stock is not found
            return HttpResponse('<h1>select a symbol you OWN</h1>')
        #gets the owned object where it's choesn by the name of the stock and the id of the user
        stock = Owned.objects.get(symbol = symbol,Username = user.id)
        #gets the shares from the form
        shares = request.POST.get('shares')
        #checks if he own enough shares
        if int(shares) > int(stock.shares):
            return HttpResponse('<h1>not enough shares/h1>')
        #uses the lookup function to return the current price of the symbol
        lookupResult = lookup(symbol)
        #calculate the user's new cash
        new_cash = float(user.cash) + ((lookupResult["price"]) * float(shares))
        #puts and saves it to the use
        user.cash = new_cash
        user.save()
        #decresaes the amount of shares the user own
        stock.shares -= int(shares)
        #if no shares delete the whole object if there is it saves
        if stock.shares == 0:
            stock.delete()
        else:
            stock.save()
        #create a new transaction and redircts to index
        Transaction.objects.create(purchase_type = 'sell',price_when_bought = lookupResult["price"], shares = shares, symbol = lookupResult["symbol"], Username = user)
        return render(request, "index.html", {})

    else:
        #sends the stocks and the balance into the form at sell.html
        context = {
            'stocks' : stocks,
            'balance' : balance,
        }
        return render(request, "sell.html", context)



# WHEN LOGIN IS IMPLEMENTED THE NEXT 2 LINES SHOULD BE UNCOMMENTED AND THE THIRD SHOULD BE DELETED
######################################@login_required
def balance_view(request):


    ############################################################# userid = session["user_id"]
    userid = request.user.id # delete this

    # get client(custom user) object inorder to access balance and other data
    c = Client.objects.get(id = userid)

    # get users balance
    userBalance = c.cash


    # if method is post
    if request.method == "POST":
        # get desired cash amount
        cash = request.POST.get("cash")

        # check input
        if not cash:
            return HttpResponse("please enter cash amount")
        if int(cash) < 0:
            return HttpResponse("invalid input")

        # check if user balance is out of bound
        userBalance = float(userBalance)
        userBalance += float(cash)
        if userBalance > 1000000000000:
            return HttpResponse("it is forbidden to be that rich")
        
        # update users cash amount
        c.cash = userBalance
        c.save()

        # redirect to index
        return redirect("/")

    # if method is get render html page
    else:
        return render(request, "balance.html",{ "balance":usd(userBalance) })



@login_required
def password_view(request):
    #this function takes 4 inputs
    if request.method == "POST":
        #get user id
        userid = request.user.id
        #get the user from the id
        og_user = Client.objects.get(id = userid)
        #gets the 4 inputs
        username = request.POST.get('username')
        old_password = request.POST.get('old_password')
        print(old_password)
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm')
        #checks for the existing of the inputs
        if not username:
            return HttpResponse('<h1>usernaeme not correct</h1>')
        if not old_password:
            return HttpResponse('<h1>old password cannot be empty</h1>')
        if not new_password:
            return HttpResponse('<h1>new password cannot be empty</h1>')
        if not confirm_password:
            return HttpResponse('<h1>new password does not match confirmation</h1>')
        #compares the old data with the new one
        if og_user.get_username() != username:
            return HttpResponse('<h1>usernaeme not correct</h1>')
        if not og_user.check_password(old_password):
            return HttpResponse('<h1>password not correct</h1>')
        if new_password != confirm_password:
            return HttpResponse('<h1>new password does not match confirmation</h1>')
        if new_password == old_password:
            return HttpResponse("<h1>new password can't be the same as the old one</h1>")
        #gets the new password and saves it then redirct to index page
        og_user.set_password(new_password)
        og_user.save()
        return render(request, "index.html", {})
    #the form with 4 inputs
    return render(request, "password.html", {})


