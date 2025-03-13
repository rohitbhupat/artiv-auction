from datetime import datetime, time
from time import localtime
import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from PIL import Image
import imagehash
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils.timezone import make_aware
import pytz
from django.urls import reverse

class Catalogue(models.Model):
    cat_name = models.CharField(max_length=255)

    def __str__(self):
        return self.cat_name

class PurchaseCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
class Artwork(models.Model):
    SALE_TYPE_CHOICES = [
        ("discount", "Discount"),
        ("auction", "Auction"),
    ]

    sale_type = models.CharField(
        max_length=50, choices=SALE_TYPE_CHOICES, default="auction"
    )
    product_id = models.CharField(max_length=255, default="", null=True)
    product_name = models.CharField(max_length=255, null=True)
    product_price = models.IntegerField(default=0, null=True)
    model_360 = models.FileField(upload_to="3d_models/", null=True, blank=True)  # 360 View Field
    opening_bid = models.IntegerField(default=0, null=True, blank=True)
    product_cat = models.ForeignKey(
        Catalogue, on_delete=models.CASCADE, null=True, blank=True
    )
    purchase_category = models.ForeignKey(  # Add this field
        PurchaseCategory, on_delete=models.CASCADE, null=True, blank=True
    )
    product_qty = models.IntegerField(default=0, null=True)
    product_image = models.ImageField(upload_to="arts/")
    dimension_unit = models.CharField(
        max_length=10, choices=[("cm", "Centimeters"), ("ft", "Feet")]
    )
    length_in_centimeters = models.FloatField(default=0, blank=True, null=True)
    width_in_centimeters = models.FloatField(default=0, blank=True, null=True)
    foot = models.FloatField(default=0, blank=True, null=True)
    inches = models.FloatField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True, db_index=True)
    favorited_by = models.ManyToManyField(User, related_name="favorite_artworks", blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    is_sold = models.BooleanField(default=False)
    is_purchased = models.BooleanField(default=False)
    status = models.CharField(
        max_length=50,
        choices=[
            ("active", "Active"),
            ("closed", "Closed"),
            ("waiting_for_response", "Waiting for Response"),
            ("unsold", "Unsold"),
        ],
        default="active",
    )
    response_deadline = models.DateTimeField(blank=True, null=True, db_index=True)
    buyer_response = models.CharField(
        max_length=11,
        choices=[("yes", "Yes"), ("no", "No"), ("no_response", "No Response")],
        default="no_response",
    )
    discounted_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    def save(self, *args, **kwargs):
        """ Automatically assign categories based on sale_type and generate a product_id. """
        if not self.product_id:  # Only generate product_id if it doesn't already exist
            self.product_id = str(uuid.uuid4())  # Generate a unique product_id using UUID

        if self.sale_type == 'discount':
            self.product_cat = None  # Ensure product_cat is empty
        elif self.sale_type == 'auction':
            self.purchase_category = None  # Ensure purchase_category is empty
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('art:catalog_products', kwargs={'pk': self.product_cat.id})
    
    def get_discounted_price(self):
        """Calculate 30% discounted price."""
        return self.product_price * 0.7

    def clean(self):
        """Validation for discount and auction artworks."""
        super().clean()

        if self.sale_type == "discount":
            self.opening_bid = None
            self.end_date = None
            if self.discounted_price is None:
                self.discounted_price = self.get_discounted_price()
            elif self.discounted_price >= self.product_price:
                raise ValidationError(
                    {
                        "discounted_price": "Discounted price must be less than the product price."
                    }
                )

        elif self.sale_type == "auction":
            if not self.product_cat:
                raise ValidationError(
                    {"product_cat": "Product category is required for bidding."}
                )
            if not self.opening_bid:
                raise ValidationError(
                    {"opening_bid": "Opening bid is required for bidding."}
                )
            if not self.end_date:
                raise ValidationError({"end_date": "End date is required for bidding."})

    def save(self, *args, **kwargs):
        """Ensure correct fields are set before saving, and check for duplicate images."""
        self.full_clean()  # Explicitly validate before saving
        
        if self.sale_type == "discount":
            self.opening_bid = None
            self.end_date = None
            self.product_cat = None  # Ensure product_cat is empty
    
            if self.discounted_price is None:
                self.discounted_price = self.get_discounted_price()
    
        elif self.sale_type == "auction":
            self.purchase_category = None  # Ensure purchase_category is empty
            if not self.opening_bid or not self.end_date:
                raise ValidationError("Opening bid and End date are required for auction.")
    
        if self.product_image:
            uploaded_image_hash = imagehash.phash(Image.open(self.product_image))
            existing_images = Artwork.objects.exclude(id=self.id)
    
            for artwork in existing_images:
                stored_image_hash = imagehash.phash(Image.open(artwork.product_image.path))
                if uploaded_image_hash == stored_image_hash:
                    raise ValidationError("Duplicate image detected. This artwork is already uploaded.")
    
        if self.end_date:
            self.end_date = timezone.make_aware(datetime.combine(self.end_date, time.min))
    
        super().save(*args, **kwargs)


    def __str__(self):
        return self.product_name

    def get_last_bid(self):
        last_bid = self.bids.order_by("-bid_amt").first()
        return last_bid.bid_amt if last_bid else self.opening_bid

    def get_total_bids(self):
        return self.bids.count()

    def mark_as_sold(self):
        self.is_sold = True
        self.save()


class OrderModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    order_date = models.DateField(auto_now_add=True)
    order_qty = models.IntegerField(default=0, null=False)
    delivery_at = models.TextField(default=" ", null=False)
    order_price = models.FloatField(default=0, null=False)

    def __str__(self):
        return f"order of {self.product} by {self.user}"


class Bid(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name="bids")
    bid_date = models.DateField(auto_now_add=True)
    bid_amt = models.IntegerField(default=1)

    def __str__(self):
        return f"bid of {self.product} on {self.bid_date}"


class Payment(models.Model):
    order = models.ForeignKey(OrderModel, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(
        _("Payment Status"), max_length=254, default="Pending", blank=False, null=False
    )
    provider_order_id = models.CharField(
        _("Order ID"), max_length=40, null=False, blank=False
    )
    payment_id = models.CharField(
        _("Payment ID"), max_length=36, null=False, blank=False
    )
    signature_id = models.CharField(
        _("Signature ID"), max_length=128, null=False, blank=False
    )
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.provider_order_id}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Artwork, on_delete=models.CASCADE, null=True, blank=True
    )  # Adjust as necessary
    message = models.TextField()
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class Query(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    query = models.TextField()
    category = models.CharField(max_length=50)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.category}"


from django.db import models


class Feedback(models.Model):
    RATING_CHOICES = [
        ("Poor", "Poor"),
        ("Fair", "Fair"),
        ("Good", "Good"),
        ("Very Good", "Very Good"),
        ("Excellent", "Excellent"),
    ]

    rating = models.CharField(
        max_length=10, choices=RATING_CHOICES, null=True, blank=True
    )
    feedback_text = models.TextField(blank=True, null=True)
    sentiment = models.CharField(
        max_length=10,
        choices=[
            ("positive", "Positive"),
            ("negative", "Negative"),
            ("neutral", "Neutral"),
        ],
        blank=True,
        null=True,
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(
        max_length=10,
        choices=[("frontend", "Frontend"), ("backend", "Backend")],
        default="frontend",
    )

    def __str__(self):
        if self.feedback_text and self.rating:
            return f"{self.rating} - {self.feedback_text[:50]}..."
        elif self.feedback_text:
            return f"{self.feedback_text[:50]}..."
        elif self.rating:
            return f"{self.rating}"
        else:
            return "No Feedback"


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=50)  # e.g., 'view', 'like', 'bid'
    timestamp = models.DateTimeField(auto_now_add=True)


class Shipping(models.Model):
    STATUS_CHOICES = [
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    order = models.OneToOneField(
        OrderModel, on_delete=models.CASCADE, related_name="shipping"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="processing"
    )
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipping for Order {self.order.id}: {self.status}"

class Refund(models.Model):
    REFUND_PERCENTAGE = {
        "processing": 1.0,  # 100% refund if processing
        "shipped": 0.6,  # 60% refund if shipped
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(OrderModel, on_delete=models.CASCADE)
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ("pending", "Pending"),
        ("processed", "Processed"),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Automatically calculate refunded amount based on order status."""
        if not self.refunded_amount:  # Calculate only if not manually set
            order_status = self.order.shipping.status  # Get order shipping status
            refund_percentage = self.REFUND_PERCENTAGE.get(order_status, 0.0)
            self.refunded_amount = self.order.total_amount * refund_percentage  # Apply percentage refund
        super().save(*args, **kwargs)

    def refund_message(self):
        """Return a message for the admin text box."""
        order_status = self.order.shipping.status
        return f"Your refund amount is ₹{self.refunded_amount} for order {self.order.id}, and it's being processed."

    def __str__(self):
        return f"Refund for {self.order} - ₹{self.refunded_amount}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'artwork')

    def __str__(self):
        return f"{self.user.username} - {self.artwork.product_name}"