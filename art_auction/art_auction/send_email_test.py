from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils.timezone import now
import pytz

class Command(BaseCommand):
    help = "Send a test email with a timestamp to verify timezone settings."

    def handle(self, *args, **kwargs):
        ist = pytz.timezone('Asia/Kolkata')
        current_time = now().astimezone(ist).strftime('%Y-%m-%d %H:%M:%S %Z')

        subject = "ARTIV EMAIL AUTOMATION TESTING"
        message = f"""Hello, Good Evening!

This is a test email to check email automation.

Current IST Time: {current_time}

Best regards,  
Artiv Auction Team"""

        recipient_list = ["bhupatrohit90@gmail.com"]  # ✅ Replace with your email

        send_mail(
            subject,  # ✅ Properly formatted subject
            message,  # ✅ Properly formatted message
            "no-reply@artiv.co.in",  # ✅ Sender email (Ensure SMTP settings allow this)
            recipient_list,
            fail_silently=False,
        )

        self.stdout.write(self.style.SUCCESS(f"✅ Test email sent successfully at {current_time} IST"))