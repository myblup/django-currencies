# -*- coding: utf-8 -*-
from logging import getLogger
from decimal import Decimal as D #, ROUND_UP

from .models import Currency as C
from .conf import SESSION_KEY

LOGGER = getLogger(__name__)

def do_calculate(price, currency):
    default = C.active.default()
    price = (D(price) / default.factor) * currency.factor
    # rounding turns 6.90 into 6.91 :duh:
    # the default HALF_EVEN rounding works fine so...
    return price.quantize(D("0.01")) #, rounding=ROUND_UP)


def calculate(price, code):
    to = C.active.get(code=code)
    return do_calculate(price, to)


def get_conversion_ratio(from_code, to_code):
    if from_code == to_code:
        return D("1.0")
    from_, to = C.active.get(code=from_code), C.active.get(code=to_code)
    return to.factor / from_.factor

def raw_convert(amount, from_code, to_code):
    if from_code == to_code:
      return amount

    ratio = get_conversion_ratio(from_code, to_code)
    amount = D(amount) * ratio
    return amount

def convert(amount, from_code, to_code):
    amount = raw_convert(amount, from_code, to_code)
    # rounding turns 6.90 into 6.91 :duh:
    # the default HALF_EVEN rounding works fine so...
    amount = amount.quantize(D("0.01")) #, rounding=ROUND_UP)
    return amount
    
def get_currency(request, raise_=False):
    for attr in ('session', 'COOKIES'):
        if hasattr(request, attr):
            try:
                code = getattr(request, attr).get(SESSION_KEY, None)
            except Exception as e:
                LOGGER.exception("failed to get currency session key '%s' from request.%s : %s", SESSION_KEY, attr, e)
                continue
            try:
                return C.active.get(code=code)
            except C.DoesNotExist as e:
                if raise_:
                    raise
                LOGGER.warning("got currency code '%s' from request but no matching active currency found", code)
                

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

def get_or_default(code):
    return C.active.get_or_default(code)
