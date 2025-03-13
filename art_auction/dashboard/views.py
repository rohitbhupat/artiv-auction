import datetime
import json
from django import forms
from art.forms import ArtworkForm, FeedbackForm
from dashboard.forms import ArtworkCreateForm, ArtworkUpdateForm
from django.views import View
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.models import (
    Artwork,
    Catalogue,
    OrderModel,
    Bid,
    Notification,
    PurchaseCategory,
    Query,
    Feedback,
    Refund,
    Shipping,
)
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    FormView,
)
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from PIL import Image
import imagehash
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings

# Set up logging
logger = logging.getLogger(__name__)


class ArtworkCreateView(LoginRequiredMixin, CreateView):
    model = Artwork
    form_class = ArtworkCreateForm  # Ensure the updated form is being used
    template_name = 'dashboard/artwork_form.html'
    success_url = reverse_lazy("dashboard:product_list")

    def get_form(self):
        form = super().get_form()
        sale_type = self.request.GET.get("filter", "discount")
        form.initial["sale_type"] = sale_type

        form.fields["purchase_category"].queryset = PurchaseCategory.objects.all()
        form.fields["product_cat"].queryset = Catalogue.objects.all()
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        sale_type = form.cleaned_data.get("sale_type")

        if sale_type == "discount":
            form.instance.opening_bid = None
            form.instance.end_date = None
        elif sale_type == "auction":
            form.instance.purchase_category = None

        return super().form_valid(form)

class ArtworkUpdateView(LoginRequiredMixin, UpdateView):
    model = Artwork
    form_class = ArtworkUpdateForm  # Use form_class instead of fields
    template_name_suffix = "_update_form"
    success_url = "/dashboard/product/"

    def get_form(self):
        form = super().get_form()
        form.fields["end_date"].widget = forms.DateInput(attrs={"type": "date"})
        return form

    def form_valid(self, form):
        # Duplicate image detection logic
        if self.request.FILES.get("product_image"):
            uploaded_image = self.request.FILES["product_image"]
            uploaded_image_hash = imagehash.phash(Image.open(uploaded_image))
            existing_artworks = Artwork.objects.exclude(id=self.object.id)

            for artwork in existing_artworks:
                stored_image_hash = imagehash.phash(
                    Image.open(artwork.product_image.path)
                )
                if uploaded_image_hash == stored_image_hash:
                    form.add_error(
                        "product_image",
                        "Duplicate image detected. This artwork has already been uploaded.",
                    )
                    return self.form_invalid(form)

        return super().form_valid(form)


class ArtworkListView(LoginRequiredMixin, ListView):
    model = Artwork
    template_name = "dashboard/artwork_list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        filter_type = self.request.GET.get("filter", "all")
        print(f"Filter type: {filter_type}")  # Debugging

        queryset = Artwork.objects.filter(
            status="active", is_sold=False, is_purchased=False
        ).order_by("-created_at")

        if filter_type == "discount":
            queryset = queryset.filter(sale_type="discount")
        elif filter_type == "auction":
            queryset = queryset.filter(sale_type="auction")
        elif filter_type == "sold":
            queryset = queryset.filter(is_sold=True)

        print(f"Queryset count: {queryset.count()}")  # Debugging
        return queryset

    # def sold_artworks(request):
    #     sold_artworks = Artwork.objects.filter(is_sold=True)
    #     context = {
    #         'sold_artworks': sold_artworks
    #     }
    #     return render(request, 'artwork_list.html', context)


class BidCreateView(LoginRequiredMixin, View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            bid_amt = float(request.POST.get("bid_amt", 0))
            product_id = request.POST.get("product")
            product_object = get_object_or_404(Artwork, pk=product_id)

            highest_bid = (
                Bid.objects.filter(product=product_object).order_by("-bid_amt").first()
            )

            # Case when there is no bid yet
            if highest_bid is None:
                min_bid = product_object.opening_bid
                if bid_amt < min_bid:
                    messages.error(
                        request,
                        "Your bid must be equal or greater than the opening bid amount.",
                    )
                    return redirect(
                        request.META.get("HTTP_REFERER", "art:artwork_detail")
                    )

            # Case when there is already a highest bid
            else:
                min_bid = highest_bid.bid_amt
                if bid_amt <= min_bid:
                    messages.error(
                        request, "Your bid must be higher than the current highest bid."
                    )
                    return redirect(
                        request.META.get("HTTP_REFERER", "art:artwork_detail")
                    )

            # If all checks pass, create the bid
            Bid.objects.create(
                user=request.user, bid_amt=bid_amt, product=product_object
            )

            # Notify previous bidders
            previous_bidders = (
                Bid.objects.filter(product=product_object)
                .exclude(user=request.user)
                .values_list("user", flat=True)
                .distinct()
            )
            for bidder in previous_bidders:
                Notification.objects.create(
                    user_id=bidder,
                    product=product_object,
                    message=f"A new bid has been placed on {product_object.product_name}",
                )

            messages.success(request, "Your bid has been placed successfully.")
            return redirect(request.META.get("HTTP_REFERER", "art:artwork_detail"))

        except Exception as e:
            logger.error(f"Error placing bid: {e}")
            messages.error(
                request,
                "An error occurred while placing your bid. Please try again later.",
            )
            return redirect(request.META.get("HTTP_REFERER", "art:artwork_detail"))


# Check auction status and notify the highest bidder
from django.utils.timezone import now


def send_purchase_email():
    products = Artwork.objects.filter(end_date__lte=now(), status="active")
    for product in products:
        highest_bid = product.bids.order_by("-bid_amt").first()
        if highest_bid:
            try:
                send_mail(
                    subject=f"You've won the auction for '{product.product_name}'!",
                    message=(
                        f"Congratulations! You've won the auction for '{product.product_name}'.\n\n"
                        f"Click here to confirm your purchase within 12 hours:\n"
                        f"http://127.0.0.1:8000/confirm_purchase/{product.product_id}/?response=yes\n\n"
                        f"Click here if you do not want to purchase:\n"
                        f"http://127.0.0.1:8000/confirm_purchase/{product.product_id}/?response=no\n\n"
                        f"You have 12 hours to respond."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[highest_bid.user.email],
                )
                logger.info(
                    f"Email sent to {highest_bid.user.email} for artwork {product.product_name}."
                )

                # Update product status and response deadline
                product.status = "waiting_for_response"
                product.response_deadline = now() + datetime.timedelta(hours=12)
            except Exception as e:
                logger.error(
                    f"Failed to send email for artwork {product.product_name}: {e}"
                )
        else:
            product.status = "unsold"

        product.save()


def handle_unsold_artworks():
    expired_artworks = Artwork.objects.filter(
        status="waiting_for_response", response_deadline__lte=now()
    )
    for artwork in expired_artworks:
        artwork.status = "unsold"
        artwork.save()
        logger.info(f"Artwork {artwork.product_name} marked as unsold.")


# Handle buyer's response
def confirm_purchase(request, artwork_id):
    response = request.GET.get("response")
    product = get_object_or_404(Artwork, pk=artwork_id)

    if response == "yes":
        product.status = "closed"
        product.buyer_response = "yes"
        product.is_sold = True
        product.save()
        return redirect("art:order_form")  # Redirect to checkout
    elif response == "no":
        product.status = "unsold"
        product.buyer_response = "no"
        product.save()
        return render(
            request,
            "art/unsold.html",
            {"message": "The artwork has been marked as unsold."},
        )
    else:
        return render(request, "dashboard/404.html", {"message": "Invalid response."})


# Move expired artworks to unsold
def check_expired_responses():
    expired_artworks = Artwork.objects.filter(
        response_deadline__lte=now(),
        status="waiting_for_response",
        buyer_response="no_response",
    )
    for product in expired_artworks:
        product.status = "unsold"
        product.save()


def latest_bid(request, pk):
    try:
        # Fetch artwork and related bid data in a single query
        artwork = get_object_or_404(Artwork, pk=pk)
        bids = Bid.objects.filter(product=artwork)

        # Get the last bid amount and total bids efficiently
        last_bid = bids.order_by("-bid_amt").first()
        total_bids = bids.count()

        # Prepare response data
        data = {
            "success": True,
            "last_bid": last_bid.bid_amt if last_bid else artwork.opening_bid,
            "total_bids": total_bids,
        }
        return JsonResponse(data)
    except Artwork.DoesNotExist:
        # Artwork not found error (should rarely happen with get_object_or_404)
        return JsonResponse(
            {"success": False, "message": "Artwork not found."}, status=404
        )
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Error fetching latest bid for artwork {pk}: {e}")
        return JsonResponse(
            {
                "success": False,
                "message": "An unexpected error occurred. Please try again later.",
            },
            status=500,
        )


class BidListView(LoginRequiredMixin, ListView):
    model = Bid
    template_name = "dashboard/bids_list.html"
    context_object_name = "bids"
    ordering = ["-bid_amt"]  # Default ordering by highest bid

    def get_queryset(self):
        queryset = super().get_queryset()

        # Handle sorting based on URL parameter 'filter'
        filter_param = self.request.GET.get("filter")
        if filter_param == "asc":
            queryset = queryset.order_by("bid_amt")  # Ascending order by bid amount
        elif filter_param == "desc":
            queryset = queryset.order_by("-bid_amt")  # Descending order by bid amount
        else:
            queryset = queryset.order_by(
                "-bid_amt"
            )  # Default to descending if no filter param

        return queryset


class ArtworkUpdateView(LoginRequiredMixin, UpdateView):
    model = Artwork
    fields = [
        "product_name",
        "product_price",
        "product_image",
        "product_cat",
        "end_date",
        "length_in_centimeters",
        "width_in_centimeters",
        "foot",
        "inches",
    ]
    template_name_suffix = "_update_form"
    success_url = "/dashboard/product/"

    def get_form(self):
        form = super().get_form()
        form.fields["end_date"].widget = forms.DateInput(attrs={"type": "date"})
        return form


class ArtworkDeleteView(LoginRequiredMixin, DeleteView):
    model = Artwork
    success_url = reverse_lazy("dashboard:product_list")


class OrderListView(LoginRequiredMixin, ListView):
    model = OrderModel
    template_name = "dashboard/ordermodel_list.html"

    def get_queryset(self):
        queryset = OrderModel.objects.all()

        # Filter orders based on user group
        if self.request.user.groups.filter(name="SellerGroup").exists():
            queryset = queryset.filter(product__user=self.request.user)
        else:
            queryset = queryset.filter(user=self.request.user)

        # Handle filtering based on the 'filter' parameter
        filter_param = self.request.GET.get("filter", "all").lower()
        if filter_param == "discount":
            queryset = queryset.filter(product__sale_type="discount")
        elif filter_param == "auction":
            queryset = queryset.filter(product__sale_type="auction")

        return queryset


# View for fetching real-time shipping status
def get_shipping_status(request, order_id):
    try:
        shipping = Shipping.objects.get(order__id=order_id)
        return JsonResponse(
            {"status": shipping.status, "tracking_number": shipping.tracking_number}
        )
    except Shipping.DoesNotExist:
        return JsonResponse(
            {"error": "Shipping details not found for this order."}, status=404
        )


# View for updating shipping status (for sellers/admins)
@csrf_exempt
def update_shipping_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order_id = data.get("order_id")
            new_status = data.get("status")

            shipping = get_object_or_404(Shipping, order__id=order_id)
            shipping.status = new_status
            shipping.save()

            return JsonResponse(
                {
                    "success": "Shipping status updated successfully!",
                    "new_status": new_status,
                }
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
@login_required
def cancel_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Get the JSON payload
            order_id = data.get("order_id")

            if not order_id:
                return JsonResponse({"error": "Order ID is required"}, status=400)

            with transaction.atomic():
                # Fetch the order
                order = get_object_or_404(OrderModel, id=order_id)

                # Fetch shipping details
                shipping = Shipping.objects.filter(order=order).first()
                if not shipping:
                    return JsonResponse(
                        {"error": "Shipping details not found"}, status=400
                    )

                status = shipping.status.lower()

                # Restrict cancellation for "Out for Delivery" and "Delivered"
                if status in ["out_for_delivery", "delivered"]:
                    return JsonResponse(
                        {"error": "Order cannot be cancelled at this stage"}, status=400
                    )

                # Determine refund amount
                if status == "processing":
                    refund_amount = order.total_price  # 100% refund
                elif status == "shipped":
                    refund_amount = order.total_price * 0.6  # 60% refund
                else:
                    refund_amount = 0

                # Create refund record
                Refund.objects.create(
                    order=order, amount=refund_amount, status="processed"
                )

                # Update order status to "Cancelled"
                shipping.status = "cancelled"
                shipping.save()

                # Mark artwork as unsold
                if hasattr(order, "artwork"):
                    order.artwork.status = "unsold"
                    order.artwork.save()

                # Return success response
                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Order #{order.id} has been cancelled successfully. Refund Amount: {refund_amount}",
                    }
                )

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


from django.views.generic import DetailView
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from dashboard.models import UserActivity, Artwork, Bid

# class ArtworkDetailView(LoginRequiredMixin, DetailView):
#     model = Artwork
#     template_name = 'art/artwork_detail.html'
#     context_object_name = 'object'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         artwork = self.get_object()

#         # Last bid and total bids logic
#         last_bid = Bid.objects.filter(product=artwork).order_by('-bid_amt').first()
#         total_bids = Bid.objects.filter(product=artwork).count()
#         context['last_bid'] = last_bid.bid_amt if last_bid else artwork.opening_bid
#         context['total_bids'] = total_bids
#         context['foot'] = artwork.foot
#         context['inches'] = artwork.inches

#         # Recommended auction artworks logic
#         context['recommended_artworks'] = self.get_auction_recommendations(artwork.id)

#         return context

#     def get_auction_recommendations(self, artwork_id):
#         try:
#             # Fetch the current artwork
#             current_artwork = Artwork.objects.get(id=artwork_id)

#             # Filter artworks in the same category and of auction type
#             recommended_artworks = Artwork.objects.filter(
#                 product_cat=current_artwork.product_cat,
#                 sale_type="auction",  # Only auction artworks
#                 is_sold=False  # Not sold
#             ).exclude(id=artwork_id)

#             # Further filter artworks with total bids <= 3
#             filtered_recommended_artworks = []
#             for artwork in recommended_artworks:
#                 total_bids = Bid.objects.filter(product=artwork).count()
#                 if total_bids <= 3:
#                     filtered_recommended_artworks.append(artwork)

#             # Return the final queryset
#             return filtered_recommended_artworks[:4]  # Limit to 4 artworks
#         except Artwork.DoesNotExist:
#             # Handle cases where the current artwork does not exist
#             return Artwork.objects.none()


def get(self, request, *args, **kwargs):
    # Record a view interaction
    artwork = self.get_object()
    UserActivity.objects.create(
        user=request.user, artwork=artwork, interaction_type="view"
    )
    return super().get(request, *args, **kwargs)


@login_required
def fetch_notifications(request):
    try:
        notifications = Notification.objects.filter(user=request.user, read=False)
        notifications_data = [
            {
                "id": n.id,
                "message": n.message,
                "timestamp": n.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "product_id": n.product.id if n.product else None,  # Include product ID
            }
            for n in notifications
        ]

        return JsonResponse({"notifications": notifications_data})
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def mark_notification_as_read(request, notification_id):
    if request.method == "POST":
        try:
            notification = get_object_or_404(
                Notification, id=notification_id, user=request.user
            )
            notification.read = True
            notification.read_at = timezone.now()
            notification.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=400
    )


@csrf_exempt
def dismiss_notification(request, notification_id):
    if request.method == "POST":
        try:
            notification = get_object_or_404(
                Notification, id=notification_id, user=request.user
            )
            notification.delete()  # Remove the notification
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=400
    )


@csrf_exempt
def clear_all_notifications(request):
    if request.method == "POST":
        try:
            notifications = Notification.objects.filter(user=request.user, read=False)
            notifications.delete()  # Remove all unread notifications
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=400
    )


from django.urls import reverse_lazy
from django.views.generic.edit import FormView
import spacy

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")


# Function to categorize the query
def categorize_query(query):
    categories = {
        "artwork quality": [
            "quality",
            "damaged",
            "broken",
            "condition",
            "flaw",
            "issue",
        ],
        "bidding issues": [
            "bid",
            "auction",
            "price",
            "update",
            "bidding error",
            "reserve",
            "winning",
        ],
        "technical support": [
            "website",
            "technical",
            "error",
            "issue",
            "bug",
            "notifications",
            "slow",
            "not working",
        ],
        "shipping and delivery": [
            "shipping",
            "delivery",
            "tracking",
            "timelines",
            "costs",
            "logistics",
            "package",
        ],
        "refund and returns": [
            "refund",
            "return",
            "canceled",
            "policy",
            "replacement",
            "compensation",
        ],
        "seller queries": [
            "seller",
            "dashboard",
            "upload",
            "artwork",
            "sales",
            "listings",
            "profit",
            "manage",
        ],
        "legal or policy concerns": [
            "copyright",
            "policy",
            "terms",
            "duplicate",
            "violation",
            "dispute",
            "legal",
        ],
        "AR and visualization": [
            "AR",
            "visualization",
            "troubleshooting",
            "feature",
            "augmented reality",
            "3D",
            "view",
        ],
        "feedback": [
            "feedback",
            "improvement",
            "ideas",
            "recommendation",
            "experience",
        ],
        "suggestions": ["suggestion"],
    }

    doc = nlp(query.lower())
    for category, keywords in categories.items():
        if any(keyword in doc.text for keyword in keywords):
            return category
    return "general"


# SubmitQueryView class
class SubmitQueryView(FormView):
    template_name = "art/contact.html"

    def post(self, request, *args, **kwargs):
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        query_text = request.POST.get("query")

        if full_name and email and query_text:
            # Categorize the query
            category = categorize_query(query_text)

            # Save the query with the category
            query = Query(
                full_name=full_name,
                email=email,
                query=query_text,
                category=category,  # Ensure 'category' is a field in your model
            )
            query.save()

            return JsonResponse({"status": "success", "category": category})
        else:
            return JsonResponse(
                {"status": "error", "message": "Invalid data submitted."}, status=400
            )


# Analyze sentiment using TextBlob
from textblob import TextBlob


def analyze_sentiment(feedback):
    if feedback:  # Ensure feedback is not empty
        analysis = TextBlob(feedback)
        return (
            "positive"
            if analysis.sentiment.polarity > 0
            else "negative" if analysis.sentiment.polarity < 0 else "neutral"
        )
    return "neutral"  # Return neutral if feedback is empty or None


def submit_feedback(request):
    if request.method == "POST":
        rating = request.POST.get("rating")  # Get rating (can be empty)
        feedback_text = request.POST.get(
            "feedback_text", ""
        ).strip()  # Get feedback text (can be empty)

        # Log the received data for debugging
        print("Rating:", rating)
        print("Feedback Text:", feedback_text)

        # Analyze sentiment if feedback text is provided
        sentiment = None
        if feedback_text:
            sentiment = analyze_sentiment(feedback_text)

        if not rating and not feedback_text:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Both rating and feedback text are empty.",
                }
            )

        # Save the feedback
        Feedback.objects.create(
            rating=rating,
            feedback_text=feedback_text,
            sentiment=sentiment,
            source="frontend",
        )

        # After submission, ensure feedback modal does not show again
        return redirect(
            "art:callback"
        )  # Redirect to callback without showing the modal again

    return JsonResponse({"status": "error", "message": "Invalid request."})


# def testmail(request):
#     send_mail(
#         'Test Mail',
#         'This is a test email',
#         'your_email@example.com',
#         ['rohit09.model@gmail.com'],
#         fail_silently=False,
#     )
#     return HttpResponse('Email sent successfully')

from django.db.models import Q


def autocomplete_artworks(request):
    query = request.GET.get("q", "").strip()
    if query:
        artworks = Artwork.objects.filter(
            Q(title__icontains=query)
            | Q(category__name__icontains=query)
            | Q(catalogue__name__icontains=query)
        ).values("id", "title")[:5]
        return JsonResponse(list(artworks), safe=False)

    return JsonResponse([], safe=False)


def get_artworks_json(request):
    try:
        artworks = list(Artwork.objects.values("id", "product_name"))  
        catalogues = list(Catalogue.objects.values("id", "cat_name"))
        purchase_category = list(PurchaseCategory.objects.values("id", "name"))

        return JsonResponse({
            "artworks": artworks,
            "catalogues": catalogues,
            "purchase_category": purchase_category
        })
    except Exception as e:
        import traceback
        error_message = str(e) + "\n" + traceback.format_exc()
        print("ERROR:", error_message)
        return JsonResponse({"error": error_message}, status=500)