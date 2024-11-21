from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password 
from django.contrib.auth import authenticate, login


from .models import Client, Owned, Transaction
from finance.helpers import lookup, usd, validatePassword, showErrorMessage
from .forms import quoteForm

# Create your views here.
@login_required  # This decorator ensures the user must be logged in to access this view
def index_view(request):
    # Retrieve the user information for the currently logged-in user
    # The 'request.user.username' refers to the username of the logged-in user.
    username = Client.objects.get(username=request.user.username)
    
    # Retrieve the amount of cash the user has (stored in the 'cash' field)
    cash = request.user.cash
    
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

        # Update the 'Transaction' model with the latest stock price for the transaction record
        # It assumes there is a transaction for each stock symbol, so it updates the 'current_price' field
        Transaction.objects.get(symbol=stock.symbol).update(current_price=stockInfo['price'])

        # Add the stock's total value to the total portfolio value (stockSum)
        stockSum += total

    # Calculate the grand total value of the user's portfolio (stocks + cash)
    grandTotal = stockSum + cash

    # Render the 'index.html' template, passing the user's wallet (stocks) and the calculated balances
    return render(request, "index.html", {
        'wallet': stocks,  # List of the user's owned stocks with updated prices and totals
        'balance': usd(cash),  # The user's available cash, formatted as USD
        'grandTotal': usd(grandTotal),  # The total value of the user's portfolio, formatted as USD
    })



@login_required
def buy_view():

    return HttpResponse('<h1>Hello World buy</h1>')


@login_required
def history_view():
    """Show history of transactions"""

    # pass data to template and render history html page
    return HttpResponse('<h1>Hello World history</h1>')



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

        # Redirect the user to the login page after successful registration.
        return redirect("/login")

    # If the request is not a POST request (i.e., the user is just visiting the page), render the registration form.
    else:
        return render(request, "register.html")
        
@login_required
def sell_view():
    """Sell shares of stock"""

    return HttpResponse('<h1>Hello World sell</h1>')



@login_required
def balance_view():

    return HttpResponse('<h1>Hello World balance</h1>')


