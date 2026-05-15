from django.db import models

class Invoice(models.Model):
    invoice_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resident = models.ForeignKey('users.Resident', on_delete=models.CASCADE)

    class Meta:
        db_table = 'invoices_invoice'

class Transaction(models.Model):
    transaction_id = models.CharField(max_length=255)
    paid_date = models.DateField()
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    slip_image_url = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

    class Meta:
        db_table = 'invoices_transaction'
