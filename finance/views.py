from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


from .models import Client, Owned, Transaction
from finance.helpers import lookup, usd
from .forms import quoteForm

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


@login_required
def quote_view(request):
    if request.method == "POST":
        form = quoteForm(request.POST)
        if form.is_valid():
            form.clean
            stock_name = form.cleaned_data['stock_name']
        result = lookup(stock_name)
        if not result:
            return render('<h1>stock not found</h1>')
        context = {
            'result' : result
        }
        return render(request, "quoted.html", context)
    else:
        form = quoteForm()
        context = {
            'form' : form
        }
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


