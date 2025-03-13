from django.db import models

class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING',
    COMPLETED = 'COMPLETED',
    FAILED = 'FAILED', 
    CANCELED = 'CANCELED', 
    SUCCESS = 'SUCCESS'
