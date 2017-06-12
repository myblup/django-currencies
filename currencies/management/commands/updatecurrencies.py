# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal as D
from datetime import datetime as d

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ImproperlyConfigured

from openexchangerates import OpenExchangeRatesClient

from ...models import Currency as C

APP_ID = getattr(settings, "OPENEXCHANGERATES_APP_ID", None)
if APP_ID is None:
    raise ImproperlyConfigured(
        "You need to set the 'OPENEXCHANGERATES_APP_ID' setting to your openexchangerates.org api key")


class Command(BaseCommand):
    help = "Update the currencies against the current exchange rates"


    def out(self, msg):
        self.stdout.write(msg.encode("ascii", "replace"))

    def handle(self, *args, **options):
        self.verbose = int(options.get('verbosity', 0))
        self.options = options

        client = OpenExchangeRatesClient(APP_ID)
        if self.verbose >= 1:
            self.out("Querying database at %s" % (client.ENDPOINT_CURRENCIES))

        try:
            code = C._default_manager.get(is_base=True).code
        except C.DoesNotExist:
            code = 'USD'  # fallback to default

        l = client.latest(base=code)

        if self.verbose >= 1 and "timestamp" in l:
            self.out("Rates last updated on %s" % (
                d.fromtimestamp(l["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")))

        if "base" in l:
            if self.verbose >= 1:
                self.out("All currencies based against %s" % (l["base"]))

            if not C._default_manager.filter(code=l["base"]):
                self.stderr.write(
                    "Base currency %r does not exist! Rates will be erroneous without it." % l["base"])
            else:
                base = C._default_manager.get(code=l["base"])
                base.is_base = True
                base.save()

        for c in C._default_manager.all():
            if c.code not in l["rates"]:
                self.stderr.write("Could not find rates for %s (%s)" % (c, c.code))
                continue

            factor = D(l["rates"][c.code]).quantize(D(".0001"))
            if c.factor != factor:
                if self.verbose >= 1:
                    self.out("Updating %s rate to %f" % (c, factor))

                C._default_manager.filter(pk=c.pk).update(factor=factor)
