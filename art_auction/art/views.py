import os
from django.conf import settings
from django.http.response import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic.base import TemplateView
from django.contrib.auth.models import Group
from django.views.generic.detail import DetailView
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from art.forms import (
    UserRegistrationForm,
    LoginForm,
    SellerInfoForm,
    UserForm,
    SellerForm,
)
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import razorpay
from django.http import JsonResponse
import re
from dashboard.models import Favorite, Payment, Artwork, OrderModel, Bid, Catalogue, PurchaseCategory
from django.views.decorators.csrf import csrf_exempt
import json
from dashboard.constants import PaymentStatus
import datetime
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

# Import the SellerInfo model
from art.models import SellerInfo, UserInfo
import logging

logger = logging.getLogger(__name__)

from django.utils import timezone
from datetime import date, timedelta

class index(View):
    def get(self, request):
        filter_param = request.GET.get("filter", "")
        current_date = date.today()  # Use date.today() to get the current date without time
        product_object_list = ''
        if filter_param == "old":
            # Define the threshold for old artworks (e.g., 1 day old)
            old_threshold_date = current_date - timedelta(days=1)
            product_object_list = Artwork.objects.filter(
                created_at__lt=old_threshold_date,
                end_date__gte=current_date,
                product_qty__gt=0,
                is_sold=False,  # Ensure only unsold artworks are considered
                sale_type="auction"  # Ensure only bidding artworks are fetched
            )
        elif filter_param == "new":
            # Define the threshold for new artworks (e.g., created in the last 1 day)
            new_threshold_date = current_date - timedelta(days=1)
            product_object_list = Artwork.objects.filter(
                created_at__gte=new_threshold_date,
                end_date__gte=current_date,
                product_qty__gt=0,
                is_sold=False,  # Ensure only unsold artworks are considered
                sale_type="auction"  # Ensure only bidding artworks are fetched
            )
        else:
            # Default view shows artworks ending today or later
            product_object_list = Artwork.objects.filter(
                end_date__gte=current_date,
                product_qty__gt=0,
                is_sold=False,  # Ensure only unsold artworks are considered
                sale_type="auction"  # Ensure only bidding artworks are fetched
            )

        # Debugging: Print out the filtered products to verify the logic
        for product in product_object_list:
            print(
                f"Product ID: {product.product_id}, Created Date: {product.created_at}, End Date: {product.end_date}, Sale Type: {product.sale_type}"
            )

        return render(
            request,
            "art/index.html",
            {
                "product_object_list": product_object_list,
                "catalogue_list": Catalogue.objects.all(),  # Adjust as per your context\
                "purchase_categories": PurchaseCategory.objects.all(),
                "current_date": current_date,
            },
        )


@login_required
def profile_settings(request):
    is_seller = request.user.groups.filter(name="SellerGroup").exists()
    user_info, created = UserInfo.objects.get_or_create(user=request.user)

    try:
        seller_info = request.user.sellerinfo
    except SellerInfo.DoesNotExist:
        seller_info = None

    # Forms
    user_form = UserForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)
    seller_form = SellerForm(instance=seller_info) if is_seller else None

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        seller_form = (
            SellerForm(request.POST, instance=seller_info) if is_seller else None
        )

        if user_form.is_valid() and (not is_seller or seller_form.is_valid()):
            user = user_form.save()
            user_info.save()

            if is_seller:
                seller_info = seller_form.save(commit=False)
                seller_info.user = user
                seller_info.save()

            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)

            messages.success(request, "Your profile has been updated successfully.")
            return redirect("art:profile_settings")
        else:
            messages.error(request, "Please correct the errors below.")

    return render(
        request,
        "art/profile_settings.html",
        {
            "userForm": user_form,
            "sellerForm": seller_form,
            "passwordForm": password_form,
            "is_seller": is_seller,
        },
    )

from django.utils.timezone import now
# Catalog View
class CatListView(View):
    def catalog_products(request, id):
        catalog = get_object_or_404(Catalogue, id=id)
        filter_option = request.GET.get("filter", "all")

        # Base queryset (including items without a product_cat)
        products = Artwork.objects.filter(
            product_qty__gt=0,
            status="active",
            is_sold=False,
            is_purchased=False
        )
        # print("Filtered Products:", products)

        # Filter for specific catalog if catalog exists
        if catalog:
            products = products.filter(product_cat=catalog)

        # Apply filters
        if filter_option == "new":
            last_7_days = now() - timedelta(days=7)
            products = products.filter(created_at__gte=last_7_days).order_by("-created_at")
        elif filter_option == "old":
            products = products.order_by("created_at")
        elif filter_option == "bidded":
            products = products.filter(id__in=Bid.objects.values_list("product_id", flat=True))

        print(f"Catalog Products: {products}")
        return render(
            request,
            "art/catalog_products.html",
            {
                "catalog": catalog,
                "product_object_list": products,
                "catalogue_list": Catalogue.objects.all(),
            },
        )


class PurchaseCategoryView(View):
    def get(self, request, id):
        purchase_category = get_object_or_404(PurchaseCategory, id=id)
        filter_option = request.GET.get("filter", "all")

        # Base queryset (including items without a purchase_category)
        products = Artwork.objects.filter(
            product_qty__gt=0,
            status="active",
            is_sold=False,
            is_purchased=False
        )
        # print("Filtered Products:", products)


        # Filter for specific purchase category if it exists
        if purchase_category:
            products = products.filter(purchase_category=purchase_category)

        # Apply filters
        if filter_option == "asc":
            products = products.order_by("end_date")
        elif filter_option == "desc":
            products = products.order_by("-end_date")

        print(f"Purchase Category Products: {products}")
        return render(
            request,
            "art/purchase_category.html",
            {
                "purchase_category": purchase_category,
                "product_object_list": products,
            },
        )


def register_user(request):
    if request.user.is_authenticated:
        return redirect("art:index")  # Redirect already logged-in users to home

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)  # Auto-login after registration
                messages.success(request, "Registration successful.")
                return redirect("art:index")  # Redirect to prevent resubmission
            except IntegrityError as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = UserRegistrationForm()

    return render(request, "art/signup.html", {"register_form": form})


class RegisterSeller(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("art:index")  # Prevent already logged-in users from registering

        userform = UserRegistrationForm()
        sellerForm = SellerInfoForm()
        return render(request, "art/registerseller.html", {"userform": userform, "sellerForm": sellerForm})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("art:index")

        userform = UserRegistrationForm(request.POST)
        sellerForm = SellerInfoForm(request.POST)

        if userform.is_valid() and sellerForm.is_valid():
            user = userform.save()
            seller_info = sellerForm.save(commit=False)
            seller_info.user = user  # Assign the newly created user
            seller_info.save()

            sellerGroup, _ = Group.objects.get_or_create(name="SellerGroup")
            user.groups.add(sellerGroup)

            login(request, user)  # Auto-login after registration
            messages.success(request, "Seller registration successful.")
            return redirect("art:index")  # Redirect to prevent resubmission

        messages.error(request, "Please correct the errors below.")
        return render(request, "art/registerseller.html", {"userform": userform, "sellerForm": sellerForm})


def user_login(request):
    if request.user.is_authenticated:
        return redirect("art:index")  # Prevent already logged-in users from logging in again

    if request.method == "POST":
        form = LoginForm(request, request.POST)
        if form.is_valid():
            uname = form.cleaned_data["username"]
            upass = form.cleaned_data["password"]
            user = authenticate(request, username=uname, password=upass)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful.")

                # Check if the user is part of the SellerGroup
                if user.groups.filter(name="SellerGroup").exists():
                    SellerInfo.objects.get_or_create(user=user)  # Ensure seller info exists

                    # Fetch related data for the seller
                    total_order = OrderModel.objects.filter(product__user=user).count()
                    total_product = Artwork.objects.filter(user=user).count()

                    return redirect("art:index")  # Redirect instead of rendering directly

                return redirect("art:index")  # Redirect to prevent resubmission

            messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = LoginForm()

    return render(request, "art/signin.html", {"login_form": form})

class Profile(LoginRequiredMixin, TemplateView):
    template_name = "social-media/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = PostObject()
        context["object_list"] = obj.get_all_posts().order_by("-created_on")
        context["business_list"] = Business.objects.all().filter(
            created_by=self.request.user
        )
        if UserProfile.objects.filter(user=self.request.user).exists():
            context["profileObj"] = UserProfile.objects.get(user=self.request.user)
            if self.request.user.userprofile.is_verified == False:
                context["is_profile_not_complete"] = True
                context["profile_form"] = UserProfileForm()
        else:
            UserProfile(user=self.request.user, dob=None, phone_number=0).save()

        return context


def logout_view(request):
    logout(request)
    return redirect("art:index")


class ArtworkDetailView(LoginRequiredMixin, DetailView):
    model = Artwork
    template_name = 'art/artwork_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artwork = self.get_object()

        # Last bid and total bids logic
        last_bid = Bid.objects.filter(product=artwork).order_by('-bid_amt').first()
        total_bids = Bid.objects.filter(product=artwork).count()
        context['last_bid'] = last_bid.bid_amt if last_bid else artwork.opening_bid
        context['total_bids'] = total_bids
        context['foot'] = artwork.foot
        context['inches'] = artwork.inches

        # Check if the user has purchased this product before
        if self.request.user.is_authenticated:
            previous_order = OrderModel.objects.filter(user=self.request.user, product=artwork).exists()
        else:
            previous_order = False

        # Recommended auction artworks logic
        context['recommended_artworks'] = self.get_auction_recommendations(artwork.id, previous_order)

        return context

    def get_auction_recommendations(self, artwork_id, previous_order):
        try:
            current_artwork = Artwork.objects.get(id=artwork_id)
    
            # Filter artworks in the same category and of auction type, excluding sold or purchased ones
            recommended_artworks = Artwork.objects.filter(
                product_cat=current_artwork.product_cat,
                sale_type="auction",  # Only auction artworks
                is_sold=False  # Not sold artworks
            ).exclude(id=artwork_id)  # Exclude the current artwork
    
            # If the user has purchased any artworks, exclude those purchased artworks
            if previous_order:
                purchased_artworks_ids = OrderModel.objects.filter(
                    user=self.request.user
                ).values_list('product__id', flat=True)
                
                # # Debugging: Check if the exclusion is happening correctly
                # print("Purchased Artworks IDs:", purchased_artworks_ids)
    
                # Exclude any purchased artworks
                recommended_artworks = recommended_artworks.exclude(id__in=purchased_artworks_ids)
    
            # Return the final queryset (limit to 4 artworks)
            return recommended_artworks[:4]
    
        except Artwork.DoesNotExist:
            # Handle cases where the current artwork does not exist
            return Artwork.objects.none()

def artwork_detail(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)
    
    # Calculate time left
    now = timezone.now()
    auction_end_time = artwork.auction_end_time

    # Live auction
    if artwork.status == 'Live':
        time_left = auction_end_time - now
        formatted_end_time = auction_end_time.strftime('%H:%M:%S')
        end_label = "Ends on"
    
    # Unsold and checking bidder eligibility
    elif artwork.status == 'Unsold':
        # This block assumes you’ve determined the user is first/second highest bidder
        formatted_end_time = '12:00 PM'
        end_label = "Ends on"
    
    # Ended auction (not unsold)
    else:
        formatted_end_time = auction_end_time.strftime('%d %b %Y, %I:%M %p')
        end_label = "Ended on"
    
    context = {
        'artwork': artwork,
        'formatted_end_time': formatted_end_time,
        'end_label': end_label,
    }
    return render(request, 'art/artwork_detail.html', context)

class UnsoldArtworkDetailView(LoginRequiredMixin, DetailView):
    model = Artwork
    template_name = 'art/unsold_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artwork = self.get_object()

        now = timezone.now()
        end_time = artwork.end_date  # Corrected usage

        # Get the highest bid
        last_bid = Bid.objects.filter(product=artwork).order_by('-bid_amt').first()
        total_bids = Bid.objects.filter(product=artwork).count()

        context['last_bid'] = last_bid.bid_amt if last_bid else artwork.opening_bid
        context['total_bids'] = total_bids
        context['formatted_end_time'] = '12:00 PM'
        context['end_label'] = 'Ends on'
        context['foot'] = artwork.foot
        context['inches'] = artwork.inches

        # Identify first and second highest bidders
        bids = Bid.objects.filter(product=artwork).order_by('-bid_amt')
        highest_bid = bids.first()
        second_highest_bid = bids[1] if bids.count() > 1 else None

        context['highest_bid'] = highest_bid
        context['second_highest_bid'] = second_highest_bid

        user = self.request.user

        # Eligibility check
        context['is_eligible'] = False
        context['eligible_rank'] = None

        if highest_bid and user == highest_bid.user:
            context['is_eligible'] = True
            context['eligible_rank'] = "first"
        elif second_highest_bid and user == second_highest_bid.user:
            context['is_eligible'] = True
            context['eligible_rank'] = "second"

        # Already purchased?
        context['already_purchased'] = OrderModel.objects.filter(user=user, product=artwork).exists()

        return context

class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        product_object = get_object_or_404(Artwork, pk=self.kwargs.get("pk"))
        last_bid = Bid.objects.filter(product=self.kwargs.get("pk")).last()
        return render(
            request=request,
            template_name="art/order_form.html",
            context={"product": product_object, "last_bid": last_bid},
        )

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Artwork, pk=request.POST["product"])
        product_price = request.POST["product_price"]
        product_qty = request.POST["product_qty"]
        delivery_at = request.POST["delivery_at"]

        order = OrderModel.objects.create(
            product=product,
            order_qty=product_qty,
            order_price=product_price,
            delivery_at=delivery_at,
            user=self.request.user,
        )

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        razorpay_order = client.order.create(
            {
                "amount": int(product_price) * int(product_qty) * 100,
                "currency": "INR",
                "payment_capture": "1",
            }
        )
        Payment.objects.create(
            order=order,
            status=PaymentStatus.PENDING,
            provider_order_id=razorpay_order["id"],
        )

        return render(
            request,
            "art/payment.html",
            {
                "callback_url": request.build_absolute_uri("/callback/"),
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": order,
                "amount_in_paise": int(product_price) * int(product_qty) * 100,
            },
        )


class SaleOrderCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        product_object = get_object_or_404(Artwork, pk=self.kwargs.get("pk"))
        previous_order = OrderModel.objects.filter(user=request.user, product=product_object).exists()

        if not previous_order:
            price = product_object.product_price * 0.8  # 20% discount
            is_first_purchase = True
        else:
            price = product_object.product_price
            is_first_purchase = False

        return render(
            request,
            "art/sale-order-form.html",
            {
                "product": product_object,
                "price": price,
                "is_first_purchase": is_first_purchase,
            },
        )

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Artwork, pk=request.POST["product"])
        product_price = request.POST["product_price"]
        product_qty = request.POST["product_qty"]
        delivery_at = request.POST["delivery_at"]

        order = OrderModel.objects.create(
            product=product,
            order_qty=product_qty,
            order_price=product_price,
            delivery_at=delivery_at,
            user=request.user,
        )

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        razorpay_order = client.order.create(
            {
                "amount": int(product_price) * int(product_qty) * 100,
                "currency": "INR",
                "payment_capture": "1",
            }
        )
        Payment.objects.create(
            order=order,
            status=PaymentStatus.PENDING,
            provider_order_id=razorpay_order["id"],
        )

        return render(
            request,
            "art/payment.html",
            {
                "callback_url": request.build_absolute_uri("/callback/"),
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": order,
                "amount_in_paise": int(product_price) * int(product_qty) * 100,
            },
        )


@csrf_exempt
def callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        return client.utility.verify_payment_signature(response_data)

    show_feedback_modal = False

    if "razorpay_signature" in request.POST:
        logger.debug(f"Received POST data: {request.POST}")

        try:
            payment_id = request.POST.get("razorpay_payment_id", "")
            provider_order_id = request.POST.get("razorpay_order_id", "")
            signature_id = request.POST.get("razorpay_signature", "")
            order_payment = Payment.objects.get(provider_order_id=provider_order_id)

            order_payment.payment_id = payment_id
            order_payment.signature_id = signature_id
            order_payment.payment_method = request.POST.get("method")
            order_payment.save()

            if verify_signature(request.POST):
                order_payment.status = PaymentStatus.SUCCESS
                show_feedback_modal = True

                product = order_payment.order.product
                product.product_qty -= int(order_payment.order.order_qty)
                if product.product_qty <= 0:
                    product.is_sold = True
                product.save()
            else:
                order_payment.status = PaymentStatus.FAILURE

            order_payment.save()

            return render(
                request,
                "art/callback.html",
                context={"status": "Payment done", "show_feedback_modal": show_feedback_modal},
            )

        except Payment.DoesNotExist:
            logger.error(f"Payment with provider_order_id {provider_order_id} does not exist.")
            return render(
                request,
                "art/callback.html",
                context={"status": "Payment failed", "error": "Invalid order ID", "show_feedback_modal": show_feedback_modal},
            )
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return render(
                request,
                "art/callback.html",
                context={"status": "Payment failed", "error": str(e), "show_feedback_modal": show_feedback_modal},
            )
    else:
        return render(
            request,
            "art/callback.html",
            context={"status": "Payment failed", "show_feedback_modal": show_feedback_modal},
        )

from django.utils.decorators import method_decorator
class ArView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        product_object = Artwork.objects.get(pk=self.kwargs.get('id'))

        # Try centimeters first
        width_m = None
        height_m = None

        if product_object.length_in_centimeters and product_object.width_in_centimeters:
            height_m = product_object.length_in_centimeters / 100
            width_m = product_object.width_in_centimeters / 100
        elif product_object.foot and product_object.inches:
            # Assuming `foot` and `inches` are used for both width and length
            width_m = (product_object.foot * 0.3048) + (product_object.inches * 0.0254)
            height_m = width_m  # If both are same; change as needed
        else:
            width_m = 1.0
            height_m = 1.0

        context = {
            "image": product_object.product_image,
            "length_in_centimeters": product_object.length_in_centimeters,
            "width_in_centimeters": product_object.width_in_centimeters,
            "foot": product_object.foot,
            "inches": product_object.inches,
            "dimension_unit": product_object.dimension_unit,
            "width_in_m": round(width_m, 2),
            "height_in_m": round(height_m, 2),
        }
        return render(request, "art/ArView.html", context)


class About(TemplateView):
    template_name = "art/about.html"


class Contact(TemplateView):
    template_name = "art/contact.html"

class Terms(TemplateView):
    template_name = "art/terms.html"
    
class Privacy(TemplateView):
    template_name = "art/privacy.html"
    
class Purchase_Cancel(TemplateView):
    template_name = "art/purchase_cancel.html"
class Auction_Cancel(TemplateView):
    template_name = "art/auction_cancel.html"
class FAQs(TemplateView):
    template_name = "art/faq.html"


# Unsold artworks view (for sellers)
class UnsoldListView(LoginRequiredMixin, ListView):
    model = Artwork
    template_name = "art/unsold.html"
    context_object_name = "object_list"

    def get_queryset(self):
        queryset = Artwork.objects.filter(end_date__lt=now(), product_qty__gt=0)

        # Get filter parameter from the request
        filter_param = self.request.GET.get("filter", "all")

        # Apply filters similar to CatListView
        if filter_param == "new":
            last_7_days = now() - timedelta(days=7)  # Adjust days as needed
            queryset = queryset.filter(created_at__gte=last_7_days).order_by("-created_at")
        elif filter_param == "old":
            queryset = queryset.order_by("created_at")  # Oldest first
        elif filter_param == "bidded":
            queryset = queryset.filter(id__in=Bid.objects.values_list("product_id", flat=True))

        return queryset
class ArtworkSaleDetailView(DetailView):
    model = Artwork
    template_name = "art/artwork-sale_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        DISCOUNT_PERCENTAGE = 20
        discount_multiplier = (100 - DISCOUNT_PERCENTAGE) / 100

        if self.request.user.is_authenticated:
            previous_order = OrderModel.objects.filter(user=self.request.user, product=product).exists()
        else:
            previous_order = False

        if previous_order:
            context["price"] = product.product_price
            context["is_first_purchase"] = False
        else:
            context["price"] = round(product.product_price * discount_multiplier, 2)
            context["is_first_purchase"] = True

        context["recommended_artworks"] = Artwork.objects.filter(
            is_sold=False,
            sale_type="discount",
        ).exclude(
            id__in=OrderModel.objects.values_list("product__id", flat=True)
        ).exclude(
            pk=product.pk
        )[:4]

        return context

class ArtworkSaleListView(LoginRequiredMixin, ListView):
    model = Artwork
    template_name = "art/artwork_sale.html"
    context_object_name = "object_list"

    def get_queryset(self):
        queryset = Artwork.objects.filter(
            product_qty__gt=0,
            is_sold=False,
            sale_type="discount",
        )

        DISCOUNT_PERCENTAGE = 20
        discount_multiplier = (100 - DISCOUNT_PERCENTAGE) / 100

        if self.request.user.is_authenticated:
            for artwork in queryset:
                previous_order = OrderModel.objects.filter(user=self.request.user, product=artwork).exists()
                if not previous_order:
                    artwork.discounted_price = round(artwork.product_price * discount_multiplier, 2)
                else:
                    artwork.discounted_price = artwork.product_price

        return queryset
@csrf_exempt
@login_required
def toggle_favorite(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            artwork_id = data.get("product_id")
            print("Received product ID:", artwork_id)  # Debugging line
            artwork = get_object_or_404(Artwork, id=artwork_id)
            favorite, created = Favorite.objects.get_or_create(user=request.user, artwork=artwork)

            if not created:
                favorite.delete()
                print("Removed from favorites")  # Debugging line
                return JsonResponse({"status": "removed"})
            print("Added to favorites")  # Debugging line
            return JsonResponse({"status": "added"})
        except Exception as e:
            print("Error:", str(e))  # Debugging line
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


@login_required
def get_favorites(request):
    favorites = Favorite.objects.filter(user=request.user).values_list('artwork__id', flat=True)
    return JsonResponse({"favorites": list(favorites)})

@login_required
def favorites_page(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('artwork')
    return render(request, 'art/favorites.html', {'favorites': favorites})

@login_required
def remove_favorite(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)
    favorite = Favorite.objects.filter(user=request.user, artwork=artwork).first()

    if favorite:
        favorite.delete()
        messages.success(request, "Artwork removed from favorites!")
    else:
        messages.warning(request, "This artwork is not in your favorites.")

    return redirect('art:favorites_page')