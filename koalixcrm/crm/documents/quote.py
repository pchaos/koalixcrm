# -*- coding: utf-8 -*-

from datetime import *
from django.db import models
from django.contrib import admin
from django.utils.translation import ugettext as _
from koalixcrm.crm.const.status import *
from koalixcrm.plugin import *
from koalixcrm.crm.documents.salesdocument import SalesDocument, OptionSalesDocument


class Quote(SalesDocument):
    valid_until = models.DateField(verbose_name=_("Valid until"))
    status = models.CharField(max_length=1, choices=QUOTESTATUS, verbose_name=_('Status'))

    def create_from_reference(self, calling_model):
        self.create_sales_document(calling_model)
        self.status = 'I'
        self.valid_until = date.today().__str__()
        self.date_of_creation = date.today().__str__()
        self.template_set = self.contract.get_template_set(self)
        self.save()
        self.attach_sales_document_positions(calling_model)
        self.attach_text_paragraphs()

    def __str__(self):
        return _("Quote") + ": " + str(self.id) + " " + _("from Contract") + ": " + str(self.contract.id)

    class Meta:
        app_label = "crm"
        verbose_name = _('Quote')
        verbose_name_plural = _('Quotes')


class OptionQuote(OptionSalesDocument):
    list_display = OptionSalesDocument.list_display + ('valid_until', 'status',)
    list_filter = OptionSalesDocument.list_filter + ('status',)
    ordering = OptionSalesDocument.ordering
    search_fields = OptionSalesDocument.search_fields
    fieldsets = OptionSalesDocument.fieldsets + (
        (_('Quote specific'), {
            'fields': ( 'valid_until', 'status', )
        }),
    )

    save_as = OptionSalesDocument.save_as
    inlines = OptionSalesDocument.inlines

    actions = ['create_purchase_confirmation', 'create_invoice',
               'create_delivery_note', 'create_purchase_order', 'create_tasks', 'create_pdf',]

    pluginProcessor = PluginProcessor()
    inlines.extend(pluginProcessor.getPluginAdditions("quoteInlines"))


class InlineQuote(admin.TabularInline):
    model = Quote
    classes = ['collapse']
    show_change_link = True
    can_delete = True
    extra = 1
    readonly_fields = (
    'description', 'contract', 'customer', 'valid_until', 'status', 'last_pricing_date', 'last_calculated_price',
    'last_calculated_tax',)
    fieldsets = (
        (_('Basics'), {
            'fields': ('description', 'contract', 'customer', 'valid_until', 'status')
        }),
        (_('Advanced (not editable)'), {
            'classes': ('collapse',),
            'fields': ('last_pricing_date', 'last_calculated_price', 'last_calculated_tax',)
        }),
    )
    allow_add = False
