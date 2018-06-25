# -*- coding: utf-8 -*-
from django.dispatch import Signal

currency_changed = Signal(providing_args=["currency_code", "request", "response",]) 
