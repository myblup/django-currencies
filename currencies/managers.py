# -*- coding: utf-8 -*-

from django.db import models


class CurrencyManager(models.Manager):

    def get_queryset(self):
        return super(CurrencyManager, self).get_queryset().filter(
            is_active=True
        )

    def default(self):
        return self.get(is_default=True)

    def base(self):
        return self.get(is_base=True)

    def get_or_default(self, code):
        try:
            return self.get(code=code)
        except self.model.DoesNotExist as e:
            return self.default()
