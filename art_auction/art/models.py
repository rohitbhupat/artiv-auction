# models.py
from django.db import models
from django.conf import settings

class SellerInfo(models.Model):
    phone_number = models.CharField(max_length=17, blank=False, default='', help_text="Please enter the phone number, without +91")
    business_name = models.CharField(max_length=255, null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sellerinfo')

    def __str__(self):
        return f'user : {self.user}'

class UserInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='userinfo')
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone_number = models.CharField(max_length=17, blank=False, default='', help_text="Please enter the phone number, without +91")
    
    def __str__(self):
        return f"User Info: {self.user}"