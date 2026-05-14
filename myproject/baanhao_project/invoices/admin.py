from django.contrib import admin

from .models import Invoice, Transaction


class TransactionInline(admin.StackedInline):
    model = Transaction
    fk_name = 'invoice'
    max_num = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'resident', 'amount', 'due_date', 'status', 'invoice_type')
    list_filter = ('status', 'invoice_type')
    search_fields = ('invoice_id',)
    inlines = [TransactionInline]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'invoice', 'paid_amount', 'payment_status', 'paid_date')
