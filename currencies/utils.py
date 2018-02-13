# -*- coding: utf-8 -*-

from decimal import Decimal as D #, ROUND_UP

from .models import Currency as C
from .conf import SESSION_KEY

def do_calculate(price, currency):
    default = C.active.default()
    price = (D(price) / default.factor) * currency.factor
    # rounding turns 6.90 into 6.91 :duh:
    # the default HALF_EVEN rounding works fine so...
    return price.quantize(D("0.01")) #, rounding=ROUND_UP)


def calculate(price, code):
    to = C.active.get(code=code)
    return do_calculate(price, to)


def convert(amount, from_code, to_code):
    if from_code == to_code:
      return amount

    from_, to = C.active.get(code=from_code), C.active.get(code=to_code)

    amount = D(amount) * (to.factor / from_.factor)
    # rounding turns 6.90 into 6.91 :duh:
    # the default HALF_EVEN rounding works fine so...
    return amount.quantize(D("0.01")) #, rounding=ROUND_UP)


def get_currency(request):
    for attr in ('session', 'COOKIES'):
        if hasattr(request, attr):
            try:
                return C.active.get(code=getattr(request, attr)[SESSION_KEY])
            except KeyError:
                continue

    # fallback to default...
    try:
        return C.active.default()
    except C.DoesNotExist:
        return None  # shit happens...

def get_currency_code(request):
    currency = get_currency(request)
    return currency.code if currency else None


def get_currency_symbol(request):
    """ return the currency symbol """
    currency = get_currency(request)
    return currency.symbol if currency else None
