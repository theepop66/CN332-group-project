from django.db import models


class Invoice(models.Model):
    """invoices_invoice — DDL."""

    class Meta:
        db_table = 'invoices_invoice'

    class InvoiceStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        OVERDUE = 'overdue', 'Overdue'
        CANCELLED = 'cancelled', 'Cancelled'

    class InvoiceType(models.TextChoices):
        MONTHLY_FEE = 'monthly_fee', 'Monthly fee'
        UTILITY = 'utility', 'Utility'
        PENALTY = 'penalty', 'Penalty'
        OTHER = 'other', 'Other'

    invoice_id = models.CharField(max_length=50, unique=True)
    resident = models.ForeignKey(
        'users.Resident',
        on_delete=models.RESTRICT,
        related_name='invoices',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.PENDING,
    )
    invoice_type = models.CharField(
        'type',
        max_length=50,
        choices=InvoiceType.choices,
        default=InvoiceType.MONTHLY_FEE,
        db_column='type',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.invoice_id


class Transaction(models.Model):
    """invoices_transaction — DDL (1:1 with invoice)."""

    class Meta:
        db_table = 'invoices_transaction'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        VERIFIED = 'verified', 'Verified'
        REJECTED = 'rejected', 'Rejected'

    transaction_id = models.CharField(max_length=50, unique=True)
    invoice = models.OneToOneField(
        Invoice,
        on_delete=models.RESTRICT,
        related_name='payment',
    )
    paid_date = models.DateField()
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    slip_image_url = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.transaction_id
