from decimal import Decimal

from django import template
from django.test import TestCase

from currencies.models import Currency
from currencies.utils import calculate, convert


class UtilsTest(TestCase):
    fixtures = ['currencies_test_data.json']
    use_transaction = False

    def test_calculate_price_success(self):
        response = calculate('10', 'USD')
        self.assertEqual(response, Decimal('15.00'))

    # def test_calculate_price_failure(self):
    #     response = calculate('10', 'EUR')
    #     self.assertEqual(response, Decimal('0.00'))

    def test_calculate_price_doesnotexist(self):
        self.assertRaises(
            Currency.DoesNotExist, calculate, '10', 'GBP')

    def test_convert_is_iso(self):
        p = Decimal("17.43")
        c1 = convert(p, "USD", "EUR")
        c2 = convert(c1, "EUR", "USD")
        self.assertEqual(p, c2)


class TemplateTagTest(TestCase):
    fixtures = ['currencies_test_data.json']
    use_transaction = False

    html = """{% load currency %}"""

    def test_currency_filter(self):
        t = template.Template(self.html +
            '{{ 10|currency:"USD" }}'
        )
        r = t.render(template.Context())
        self.assertEqual(u'15.00', r.replace(",", "."))

    def test_currency_filter_when_price_is_none(self):
        t = template.Template(self.html +
            '{{ price|currency:"USD" }}'
        )
        r = t.render(template.Context({"price":None}))
        self.assertEqual(u'', r)


    def test_change_currency_tag_success(self):
        t = template.Template(self.html +
            '{% change_currency 10 "USD" %}'
        )
        r = t.render(template.Context())
        self.assertEqual(u'15.00', r.replace(",", "."))

    # def test_change_currency_tag_failure(self):
    #     t = template.Template(self.html +
    #         '{% change_currency 10 "GPB" %}'
    #     )
    #     self.assertEqual(t.render(template.Context()), u'0.00')
