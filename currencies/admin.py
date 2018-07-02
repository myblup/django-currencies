# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Currency

def annotate(description):
    def wrapper(func):
        func.short_description = description
        return func
    return wrapper

@annotate("activate selected currencies")
def activate(modeladmin, request, queryset):
    queryset.update(is_active=True)

@annotate("deactivate selected currencies")
def deactivate(modeladmin, request, queryset):
    queryset.update(is_active=False)




class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "symbol", "is_active", "is_base", "is_default",  "factor")
    list_filter = ("is_active", )
    search_fields = ("name", "code")

    actions = [activate, deactivate]


admin.site.register(Currency, CurrencyAdmin)
