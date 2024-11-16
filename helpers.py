import csv
import requests
import urllib
import uuid
from dotenv import load_dotenv
import json
import os

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Prepare API request
    symbol = symbol.upper()

    # # Load environment variables from the .env file
    # load_dotenv()

    # # Retrieve the API key
    # api_key = os.getenv('API_KEY')

    # # Yahoo Finance API
    # url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={urllib.parse.quote_plus(symbol)}&apikey={urllib.parse.quote_plus(api_key)}'

    # Query API
    try:
        # response = requests.get(
        #     url,
        #     cookies={"session": str(uuid.uuid4())},
        #     headers={"Accept": "*/*", "User-Agent": "python-requests"},
        # )
        # response.raise_for_status()

        # data = response.json()
        # price = round(float(data['Global Quote']['05. price']), 2)
        with open('stocks.json', 'r') as file:
            data = json.load(file)
        price = next(stock['price'] for stock in data['stocks'] if stock['symbol'] == symbol)
        return {"price": price, "symbol": symbol}
    except (KeyError, IndexError, requests.RequestException, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
