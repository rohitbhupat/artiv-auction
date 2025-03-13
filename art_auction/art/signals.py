from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserInfo, SellerInfo
from django.utils.timezone import now, timedelta
from django.core.mail import send_mail
from dashboard.models import Artwork
from django.conf import settings

@receiver(post_save, sender=User)
def create_user_info(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        UserInfo.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def create_seller_info(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        SellerInfo.objects.get_or_create(user=instance)

# @receiver(post_save, sender=Artwork)
# def auction_end_handler(sender, instance, **kwargs):
#     # Check if the auction ended and the status is still 'active'
#     if instance.end_date <= now().date() and instance.status == 'active':
#         # Get the highest bid
#         highest_bid = instance.bids.order_by('-bid_amt').first()

#         if highest_bid:
#             # Send email to the highest bidder
#             send_mail(
#                 subject=f"Congratulations! You've won the auction for '{instance.product_name}'!",
#                 message=(
#                     f"Dear {highest_bid.user.username},\n\n"
#                     f"You've won the auction for '{instance.product_name}' with a bid of ₹{highest_bid.bid_amt}.\n\n"
#                     f"Please confirm your purchase within 12 hours using the following link:\n"
#                     f"http://127.0.0.1:8000/confirm_purchase/{instance.id}/?response=yes\n\n"
#                     f"Decline by clicking here:\n"
#                     f"http://127.0.0.1:8000/confirm_purchase/{instance.id}/?response=no\n\n"
#                     f"If no response is received within 12 hours, the artwork will be marked as unsold."
#                 ),
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[highest_bid.user.email],
#             )
#             # Update the artwork status
#             instance.status = 'waiting_for_response'
#             instance.response_deadline = now() + timedelta(hours=12)
#         else:
#             # If no bids, mark artwork as unsold
#             instance.status = 'unsold'
#         instance.save()