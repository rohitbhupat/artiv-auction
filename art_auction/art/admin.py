from django.contrib import admin
from art.models import SellerInfo
from dashboard.models import Artwork, Refund
from .forms import ArtworkForm, RefundAdminForm  # Import the ArtworkForm
from django.utils.html import format_html

class ArtworkAdmin(admin.ModelAdmin):
    form = ArtworkForm
    
    list_display = ("product_name", "sale_type", "product_price", "purchase_category", "is_sold")
    list_filter = ("sale_type", "purchase_category", "is_sold")
    search_fields = ("product_name", "purchase_category__name") 

    class Media:
        js = ('js/admin_dimension_toggle.js',)  # Ensure the path is correct

    def save_model(self, request, obj, form, change):
        if not obj.sale_type:  # Ensure sale_type is set
            obj.sale_type = 'auction'  # Default to auction

        if obj.sale_type == 'discount' and obj.product_price:
            obj.discounted_price = obj.product_price * 0.7  # Apply 30% discount

        if not obj.user:
            obj.user = request.user  # Assign current user if not set
            
        if obj.sale_type == "discount":
            obj.opening_bid = None
            obj.end_date = None
        elif obj.sale_type == "auction":
            obj.purchase_category = None

        super().save_model(request, obj, form, change)


    def get_changeform_initial_data(self, request):
        """Set default values when adding a new artwork."""
        return {'sale_type': 'auction'}

    def get_fieldsets(self, request, obj=None):
        if obj and obj.sale_type == 'discount':
            return (
                (None, {
                    'fields': (
                        'sale_type', 'product_name', 'product_price', 'purchase_category', 'discounted_price',
                        'product_qty', 'product_image', 'model_360', 'dimension_unit', 
                        'length_in_centimeters', 'width_in_centimeters', 'foot', 'inches',
                    )
                }),
            )
        elif obj and obj.sale_type == 'auction':
            return (
                (None, {
                    'fields': (
                        'sale_type', 'product_name', 'opening_bid', 'product_cat', 'purchase_category',
                        'product_qty', 'product_image', 'model_360', 'end_date',
                        'dimension_unit', 'length_in_centimeters', 'width_in_centimeters', 'foot', 'inches',
                    )
                }),
            )
    
        return super().get_fieldsets(request, obj)


class RefundAdmin(admin.ModelAdmin):
    form = RefundAdminForm
    list_display = ("user", "order", "refunded_amount", "status", "refund_message_display")
    readonly_fields = ("refund_message_display", "refunded_amount")  # Make the refunded amount read-only in the admin

    def refund_message_display(self, obj):
        """Show refund message in Django admin."""
        return format_html(f'<p style="color:blue;">{obj.refund_message()}</p>')

    refund_message_display.short_description = "Refund Notification"

    def save_model(self, request, obj, form, change):
        """Trigger notification when a refund is processed."""
        if obj.status == "processed":
            # Logic to trigger a frontend notification (e.g., WebSockets, Firebase, etc.)
            print(f"Notification: Refund processed for Order {obj.order.id}")
        super().save_model(request, obj, form, change)

admin.site.register(Refund, RefundAdmin)
admin.site.register(Artwork, ArtworkAdmin)
admin.site.register(SellerInfo)