import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # get balance and set constants
    userid = session["user_id"]
    idd = userid
    balance = db.execute("SELECT cash FROM users WHERE id = ? ", idd)
    username = db.execute("SELECT username FROM users WHERE id = ?", idd)
    stocks = db.execute("SELECT * FROM owned WHERE username = ?", username[0]['username'])
    stockSum = 0

    # update stock price
    for stock in stocks:
        stockInfo = lookup(stock['symbol'])
        total = float(stockInfo['price']) * float(stock["shares"])
        db.execute("UPDATE owned SET stock_price = ? WHERE symbol = ?", usd(stockInfo['price']), stockInfo["symbol"])
        db.execute("UPDATE owned SET total = ? WHERE symbol = ?", usd(total), stockInfo["symbol"])
        db.execute("UPDATE transactions SET current_price = ? WHERE symbol = ?", usd(stockInfo['price']), stockInfo['symbol'])
        stockSum += total
    grandTotal = stockSum + balance[0]['cash']

    # get updates stock info
    updatedStocks = db.execute("SELECT * FROM owned WHERE username = ?", username[0]['username'])

    # render with balance and owned stocks
    return render_template("index.html", wallet=updatedStocks, balance=usd(balance[0]['cash']), grandTotal=usd(grandTotal))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # get users balance
    userid = session["user_id"]
    balance = db.execute("SELECT cash FROM users WHERE id = ? ", userid)
    # if method is get
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        ptype = "Buy"
        lookupResult = lookup(symbol)
        # check input
        if not symbol:
            return apology("Please enter stock symbol", 400)
        if not shares:
            return apology("please enter shares amount", 400)
        if not shares.isnumeric():
            return apology("please enter whole number", 400)
        if float(shares) <= 0:
            return apology("Invalid input", 400)
        if not lookupResult:
            return apology("Invalid stock symbol", 400)
        # see cost and check if user can afford it
        purchasePrice = float(lookupResult["price"]) * float(shares)
        stockPrice = lookupResult["price"]
        if purchasePrice > balance[0]['cash']:
            return apology("You don't have enough balance", 400)
        # get username
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
        # add purchase to db and update users balance
        db.execute("INSERT INTO transactions (purchase_type, price_when_bought, current_price, shares, symbol, username, time) VALUES(?, ?, ?, ?, ?, ?, DATETIME('now'))",
                   ptype, usd(stockPrice), usd(stockPrice), shares, symbol, username[0]['username'])
        db.execute("UPDATE users SET cash = ?", (balance[0]['cash'] - purchasePrice))
        # update users wallet
        owned_ids = db.execute("SELECT id FROM owned WHERE symbol = ?", symbol)
        if not owned_ids:
            db.execute("INSERT INTO owned (symbol, shares, stock_price, total, username) VALUES(?, ?, ?, ?, ?)",
                       symbol, shares, usd(stockPrice), usd(purchasePrice),  username[0]['username'])
        else:
            oldShares = db.execute("SELECT shares FROM owned WHERE symbol = ?", symbol)
            newShares = int(oldShares[0]['shares']) + int(shares)
            db.execute("UPDATE owned SET shares = ? WHERE symbol = ?", newShares, symbol)
            db.execute("UPDATE owned SET total = ? WHERE symbol = ?", usd(stockPrice * newShares), symbol)
        # redirect to main page
        return redirect("/")
    else:
        # render buy template
        return render_template("buy.html", balance=usd(balance[0]['cash']))


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # get username and extract data from db
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    transactions = db.execute("SELECT * FROM transactions WHERE username = ?", username[0]['username'])

    # pass data to template and render history html page
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # if method is post
    if request.method == "POST":
        symbol = request.form.get("symbol")
        # lookup symbol and make sure it exists
        lookupResult = lookup(symbol)
        if not lookupResult:
            return apology("Stock symbol does not exist", 400)
        # load up quote page
        stockSymbol = lookupResult['symbol']
        stockPrice = lookupResult['price']
        return render_template("quoted.html", symbol=stockSymbol, price=usd(stockPrice))

    # if method is get
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # if method is post
    if request.method == "POST":
        # store input in variables
        username = request.form.get("username")
        password = request.form.get("password")
        confirmPass = request.form.get("confirmation")
        passwordHash = generate_password_hash(password)
        usernameDuplicate = db.execute("SELECT username FROM users WHERE username = ?", username)
        print(usernameDuplicate)

        # check input
        if not username:
            return apology("Please fill in a username", 400)
        if not password:
            return apology("Please fill in a password", 400)
        if usernameDuplicate:
            return apology("Username already taken", 400)
        if password != confirmPass:
            return apology("Password doesn't match", 400)

        # insert user data to database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, passwordHash)

        # log user in and activate cookies
        userid = db.execute("SELECT id FROM users WHERE username = ? AND hash = ?", username, passwordHash)
        session["user_id"] = userid

        return redirect("/register")

    # if method is get
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # Get users username
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    # get users balance
    userid = session["user_id"]
    balance = db.execute("SELECT cash FROM users WHERE id = ? ", userid)
    userBalance = balance[0]['cash']
    ownedStockss = db.execute("SELECT symbol FROM owned WHERE username = ?", username[0]['username'])
    # if method is post
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        ptype = "Sell"
        lookupResult = lookup(symbol)
        ownedSharesdb = db.execute("SELECT shares FROM owned WHERE symbol = ?", symbol)

        # check input
        if not symbol:
            return apology("Please enter stock symbol", 400)
        if not shares:
            return apology("please enter shares amount", 400)
        if not lookupResult:
            return apology("Invalid stock symbol", 400)
        if int(shares) < 0:
            return apology("Can't sell negative stocks", 400)

        # define owned shares and stock price after verification to prevent error
        ownedShares = ownedSharesdb[0]['shares']
        stockPrice = lookupResult['price']

        # check if user has enough shares
        if int(shares) > ownedShares:
            return apology("You don't own enough shares", 400)

        # get new data
        newShares = ownedShares - int(shares)
        newTotal = stockPrice * newShares

        # Insert transaction into db
        db.execute("INSERT INTO transactions (purchase_type, price_when_bought, current_price, shares, symbol, username, time) VALUES(?, ?, ?, ?, ?, ?, DATETIME('now'))",
                   ptype, usd(stockPrice), usd(stockPrice), shares, symbol, username[0]['username'])

        # if there are no stock left: delete from owned db
        if newShares <= 0:
            db.execute("DELETE FROM owned WHERE symbol = ? AND username = ?", symbol, username[0]['username'])

        # else update wallet
        else:
            db.execute("UPDATE owned SET shares = ? , total = ? WHERE symbol = ? AND username = ?",
                       newShares, usd(newTotal), symbol, username[0]['username'])

        # update users balance
        purchasePrice = float(shares) * stockPrice
        userBalance = userBalance + purchasePrice
        db.execute("UPDATE users SET cash = ?", userBalance)

        # redirect to index page
        return redirect("/")

    else:
        return render_template("sell.html", balance=usd(userBalance), stocks=ownedStockss)


@app.route("/balance", methods=["GET", "POST"])
@login_required
def balance():

    # get users balance
    userid = session["user_id"]
    balance = db.execute("SELECT cash FROM users WHERE id = ? ", userid)
    userBalance = balance[0]['cash']

    # if method is post
    if request.method == "POST":
        # get desired cash amount and credit card info and username
        cash = request.form.get("cash")
        credit = request.form.get("credit")
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])

        # check input
        if not cash:
            return apology("please enter cash amount", 403)
        if not credit:
            return apology("please enter credit card info(please don't)", 403)
        if int(cash) < 0:
            return apology("invalid input", 403)
        if int(credit) < 0:
            return apology("invalid input", 403)

        # add desired abount to users balance
        userBalance += float(cash)
        db.execute("UPDATE users SET cash = ? WHERE username = ?", userBalance, username[0]['username'])

        # redirect to index
        return redirect("/")

    # if method is get render html page
    else:
        return render_template("balance.html", balance=usd(userBalance))

@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    if request.method == "POST":

        username = request.form.get("username")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) < 1:
            return ("input a vaild username")
        
        if username != (db.execute("SELECT username FROM users WHERE id = ?", session['user_id'])[0]['username']):
            return render_template("error.html",error = "username doesn't match")
        
        old_password = request.form.get("old_password")

        if  rows[0]["password"]  != old_password:
            return render_template("error.html",error ="password doesn't match")
        
        new_password = request.form.get("new_password")

        if not new_password:
            return render_template("error.html",error ="empty new password")
        
        confirm = request.form.get("confirm")

        if not confirm:
            return render_template("error.html",error ="empty confirm")
        
        if new_password != confirm:
            return render_template("error.html",error ="new password doesn't match confirmation")
        
        if new_password == old_password:
            return render_template("error.html",error ="new password can't be the same as the old one")

        db.execute("UPDATE users SET password = (?) WHERE username = (?)", new_password, username)

        return redirect("/")
    
    else:
        return render_template("password.html")