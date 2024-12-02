import csv
import requests
import urllib
import uuid
from dotenv import load_dotenv
import json
import os

from django.shortcuts import render, redirect
from functools import wraps

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
        with open('stocks.json', 'r',) as file:
            data = json.load(file)
        price = next(stock['price'] for stock in data['stocks'] if stock['symbol'] == symbol)
        return {"price": price, "symbol": symbol}
    except:
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def validatePassword(password):
    """Validate the password based on specific rules."""
    
    # Check if the password length is less than 8 characters
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    
    # Initialize flags to track if the password has required character types
    has_digit = False
    has_upper = False
    has_lower = False
    has_symbol = False

    # Loop through each character in the password to check for the required conditions
    for char in password:
        if char.isdigit():  # Checks if the character is a number (0-9)
            has_digit = True
        elif char.isupper():  # Checks if the character is an uppercase letter (A-Z)
            has_upper = True
        elif char.islower():  # Checks if the character is a lowercase letter (a-z)
            has_lower = True
        elif not char.isalnum():  # Checks for non-alphanumeric characters (symbols like @, $, etc.)
            has_symbol = True

        # If all conditions are met, exit the loop early for efficiency
        if has_digit and has_upper and has_lower and has_symbol:
            break

    # Return specific error messages if any required condition is not met
    if not has_digit:
        return "Password must contain at least one number."
    if not has_upper:
        return "Password must contain at least one uppercase letter."
    if not has_lower:
        return "Password must contain at least one lowercase letter."
    if not has_symbol:
        return "Password must contain at least one symbol."

    # If all conditions are met, return None indicating the password is valid
    return None


def showErrorMessage(request, html, errorMessage):
    
    # This function takes in the request object, the HTML template to render, 
    # and an error message to display to the user.
    return render(request, html, {'errorMessage': errorMessage})


def showErrorMessageContext(request, html, errorMessage, context):
    # This function takes in the request object, the HTML template to render, 
    # and the context + an error message to display to the user.
    context['errorMessage'] = errorMessage
    return render(request, html, context)