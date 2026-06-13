# models.py
from django.db import models
from django.conf import settings

class SellerInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sellerinfo')

    def __str__(self):
        return f'user : {self.user}'

class UserInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='userinfo')
    email = models.EmailField(max_length=254, blank=True, null=True)

    def __str__(self):
        return f"User Info: {self.user}"