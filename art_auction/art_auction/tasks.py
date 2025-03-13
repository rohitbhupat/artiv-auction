from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from dashboard.models import Auction

@shared_task
def send_end_auction_email(auction_id):
    auction = Auction.objects.get(id=auction_id)
    highest_bidder = auction.bids.order_by('-amount').first().user
    subject = f"Congratulations on winning the auction for {auction.item.name}"
    message = f"Dear {highest_bidder.username},\n\nYou have won the auction for {auction.item.name} with a bid of ${auction.highest_bid}.\nPlease proceed to checkout to complete your purchase."

    # Send the email
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [highest_bidder.email])
    
    return f"Email sent to {highest_bidder.username}"
