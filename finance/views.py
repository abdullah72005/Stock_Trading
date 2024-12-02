from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password 
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.template import engines

from .models import Client, Owned, Transaction, Portfolio
from finance.helpers import lookup, usd, validatePassword, showErrorMessage, showErrorMessageContext 

# Create your views here.
@login_required  # This decorator ensures the user must be logged in to access this view
def index_view(request):
    # Retrieve the user information for the currently logged-in user
    # The 'request.user.username' refers to the username of the logged-in user.
    username = Client.objects.get(username=request.user.username)
    
    # Retrieve the amount of cash the user has (stored in the 'cash' field)
    cash = username.get_cash()
    
    # Retrieve all stocks that the user owns by using the related 'owned_stocks' field from the Client model
    stocks = username.owned_stocks.all()

    # Initialize a variable to keep track of the total value of the user's stocks
    stockSum = 0

    # Loop through each stock owned by the user to calculate its total value
    for stock in stocks:
        # Retrieve the latest stock information from the API
        stockInfo = lookup(stock.symbol)
        
        # Calculate the total value of the stock (shares * current stock price)
        total = float(stockInfo['price']) * float(stock.shares)
        
        # Update the stock's stored price and total value in the database
        stock.stock_price = stockInfo['price']
        stock.total = total
        
        # Save the updated stock information in the database
        stock.save()

        # Add the stock's total value to the total portfolio value (stockSum)
        stockSum += total

    # if user has no portofolio make one
    try:
        portfolio = Portfolio.objects.get(Username=username)
    except:
        portfolio = Portfolio(Username=username)
        portfolio.save()

    # Calculate the grand total value of the user's portfolio (stocks + cash) and add it to db
    portfolio.set_net_worth(stockSum + float(cash))
    portfolio.save()

    # Render the 'index.html' template, passing the user's wallet (stocks) and the calculated balances
    return render(request, "index.html", {
        'wallet': stocks,  # List of the user's owned stocks with updated prices and totals
        'balance': usd(cash),  # The user's available cash, formatted as USD
        'grandTotal': usd(portfolio.get_net_worth()),  # The total value of the user's portfolio, formatted as USD
    })



@login_required

def buy_view(request):
    """Buy shares of stock"""
    
    # get user id
    userid = request.user.id 

    # get client(custom user) object inorder to access balance and other data
    c = Client.objects.get(id = userid)

    # get users balance
    balance = c.get_cash()
    #gets the context for the buy.html to render Correctly
    context = {
        'balance' : usd(balance),
    }

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
            return showErrorMessageContext(request, "buy.html", "Please enter stock symbol", context)
        if not shares:
            return showErrorMessageContext(request, "buy.html", "please enter shares amount", context)
        if not shares.isnumeric():
            return showErrorMessageContext(request, "buy.html", "please enter whole number", context)
        if float(shares) <= 0:
            return showErrorMessageContext(request, "buy.html", "Invalid input", context)
        if not lookupResult:
            return showErrorMessageContext(request, "buy.html", "Invalid stock symbol", context)
        
        # see cost and check if user can afford it
        purchasePrice = float(lookupResult["price"]) * float(shares)
        stockPrice = lookupResult["price"]
        if purchasePrice > balance:
            return showErrorMessageContext(request, "buy.html", "You don't have enough balance", context)
        
        # add purchase to db
        trans = Transaction(purchase_type=ptype, price_when_bought=stockPrice, shares=shares, symbol=symbol, Username=c)
        trans.save()

        # update users balance
        c.set_cash(float(balance) - purchasePrice) 
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
        return render(request, "buy.html", context)




@login_required
def history_view(request):
    """Show history of transactions"""

    # get user id
    userid = request.user.id 


    # get client(custom user) object inorder to use as foreign key in transactions
    c = Client.objects.get(id = userid)

    # get all user transactions
    transactions = Transaction.objects.filter(Username=c)

    # pass data to template and render history html page
    return render(request, "history.html", {"transactions":transactions})



def login_view(request):

    # Check if the request is a POST request (i.e., the user has submitted the login form).
    if request.method == "POST":
        # Get the username and password entered by the user from the form.
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check if the username was provided by the user. If not, show an error message.
        if not username:
            return showErrorMessage(request, "login.html", "Please Enter a username")

        # Check if the password was provided by the user. If not, show an error message.
        elif not password:
            return showErrorMessage(request, "login.html", "Please Enter a password")

        # Try to find a user (client) with the provided username in the database.
        # If the username doesn't exist, an exception is raised.
        try:
            client = Client.objects.get(username=username)
        except Client.DoesNotExist:
            # If the username does not exist, show an error message.
            return showErrorMessage(request, "login.html", "Invalid Username.")

        # If the username exists, check if the password entered by the user matches the stored password.
        # The check_password function compares the plaintext password with the hashed password stored in the database.
        if check_password(password, client.password):
            # If the password matches, authenticate the user.
            # The authenticate function checks the username and password against the database.
            user = authenticate(request, username=client.username, password=password)

            # If the authentication is successful, 'user' will be a valid user object.
            if user is not None:
                # Log the user in by storing their session information.
                login(request, user)

                # After logging in, redirect the user to the home page (or another page).
                return redirect("/")

            else:
                # If authentication failed, show an error message.
                return showErrorMessage(request, "login.html", "Authentication failed.")
        else:
            # If the password is incorrect, show an error message.
            return showErrorMessage(request, "login.html", "Invalid password.")
    
    # If the request is not a POST request (i.e., the user is just visiting the page), render the login form.
    else:
        return render(request, "login.html")



def logout_view(request):
    """Log user out"""

    # Forget any user_id
    request.session.flush()

    # Redirect user to login form
    return redirect("/login")

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
            return showErrorMessage(request, "quote.html", 'stock not found')
        context = {
            'result' : result
        }
        # if found it renders the new page which tells the price
        return render(request, "quoted.html", context)
    else:
        return render(request, "quote.html", {})



def register_view(request):

    # Check if the request is a POST request (i.e., a form submission).
    if request.method == "POST":
        # Get the values entered by the user for username, password, and password confirmation from the form.
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirmPassword = request.POST.get("confirmation")

        # Check if the username already exists in the database by querying the 'Client' table.
        usernameDuplicate = Client.objects.filter(username=username)

        # If the username is empty, show an error message and return to the register page.
        if not username:
            return showErrorMessage(request, "register.html", "Please fill in a username")

        # If the username is already taken, show an error message and return to the register page.
        if usernameDuplicate:
            return showErrorMessage(request, "register.html", "Username already taken")

        # If the password is empty, show an error message and return to the register page.
        if not password:
            return showErrorMessage(request, "register.html", "Please fill in a password")

        # Validate the password for strength (this function checks for things like length, special characters, etc.).
        errorMessage = validatePassword(password)
        
        # If the password doesn't meet the validation criteria, show an error message and return to the register page.
        if errorMessage:
            return showErrorMessage(request, "register.html", errorMessage)

        # Check if the password and the confirmation password match.
        if password != confirmPassword:
            return showErrorMessage(request, "register.html", "Please make sure the confirmation password matches the original password")

        # If all checks pass, create a new 'Client' object and save the user to the database.
        # The password is hashed using 'make_password' to store it securely.
        client = Client(username=username, password=make_password(password))
        client.save()  # Save the new user to the database.

        # initialize portofolio obj in db
        portfolio = Portfolio(Username=client)
        portfolio.save()

        # Redirect the user to the login page after successful registration.
        return redirect("/login")

    # If the request is not a POST request (i.e., the user is just visiting the page), render the registration form.
    else:
        return render(request, "register.html")
        
@login_required
def sell_view(request):
    """Sell shares of stock"""

    #gets user id
    userid = request.user.id
    #gets current user from id
    user = Client.objects.get(id = userid)
    #gets the user's cash amount
    balance = user.get_cash()
    #gets all the stocks the user have
    stocks = Owned.objects.filter(Username = user.id)

    #sends the stocks and the balance into the form at sell.html
    context = {
        'stocks'  : stocks,
        'balance' : usd(balance),
    }

    if request.method == "POST":
        #gets the symbol choesn from the form
        symbol = request.POST.get('symbol')
        #checks if the user inputs a symbol
        if not symbol:
            return showErrorMessageContext(request, "sell.html", 'select a symbol', context)
            #checks if the user owns this symbol
        try:
            stock = get_object_or_404(stocks, symbol=symbol) 
        except: # Handle the case where the stock is not found
            return showErrorMessageContext(request, "sell.html", 'select a symbol you OWN', context)
        #gets the owned object where it's choesn by the name of the stock and the id of the user
        stock = Owned.objects.get(symbol = symbol,Username = user.id)
        #gets the shares from the form
        shares = request.POST.get('shares')
        #checks if he own enough shares
        if int(shares) > int(stock.shares):
            return showErrorMessageContext(request, "sell.html", 'not enough shares', context)
        #uses the lookup function to return the current price of the symbol
        lookupResult = lookup(symbol)
        #calculate the user's new cash
        new_cash = float(user.get_cash()) + ((lookupResult["price"]) * float(shares))
        #puts and saves it to the use
        user.set_cash(new_cash)
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
        return redirect("/")

    else:
        return render(request, "sell.html", context)



@login_required
def balance_view(request):

    # get user id
    userid = request.user.id 

    # get client(custom user) object inorder to access balance and other data
    c = Client.objects.get(id = userid)

    # get users balance
    userBalance = c.get_cash()

    #gets the context for the balance.html to render Correctly
    context = {
        'balance': usd(userBalance)
    }

    # if method is post
    if request.method == "POST":
        # get desired cash amount
        cash = request.POST.get("cash")

        # check input
        if not cash:
            return showErrorMessageContext(request, "balance.html", "please enter cash amount", context)
        if int(cash) < 0:
            return showErrorMessageContext(request, "balance.html", "invalid input", context)

        # check if user balance is out of bound
        userBalance = float(userBalance)
        userBalance += float(cash)
        if userBalance > 1000000000000:
            return showErrorMessageContext(request, "balance.html", "it is forbidden to be that rich", context)
        
        # update users cash amount
        c.set_cash(userBalance)
        c.save()

        # redirect to index
        return redirect("/")

    # if method is get render html page
    else:
        return render(request, "balance.html", context)



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
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm')
        #checks for the existing of the inputs
        if not username:
            return showErrorMessage(request, "password.html", 'username not correct')
        if not old_password:
            return showErrorMessage(request, "password.html", 'old password cannot be empty')
        if not new_password:
            return showErrorMessage(request, "password.html", 'new password cannot be empty')
        if not confirm_password:
            return showErrorMessage(request, "password.html", 'new password does not equal confirmation')
        #compares the old data with the new one
        if og_user.get_username() != username:
            return showErrorMessage(request, "password.html", 'usernaeme not correct')
        if not og_user.check_password(old_password):
            return showErrorMessage(request, "password.html", 'password not correct')
        if new_password != confirm_password:
            return showErrorMessage(request, "password.html", 'new password does not match confirmation')
        if new_password == old_password:
            return showErrorMessage(request, "password.html", "new password can't be the same as the old one")
        #gets the new password and saves it then redirct to index page
        og_user.set_password(new_password)
        og_user.save()
        return redirect("/")
    #the form with 4 inputs
    return render(request, "password.html", {})


