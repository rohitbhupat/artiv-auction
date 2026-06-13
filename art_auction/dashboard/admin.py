from django.contrib import admin
from .models import Catalogue, OrderModel, Payment, Shipping, Bid, Query, Notification, Feedback, PurchaseCategory, Favorite
from django.db.models import Count, Q
from django.utils.safestring import mark_safe


# Register your models here.
admin.site.register(PurchaseCategory)
admin.site.register(Favorite)
admin.site.register(Catalogue)
admin.site.register(OrderModel)
admin.site.register(Payment)
admin.site.register(Shipping)
admin.site.register(Bid)
admin.site.register(Notification)

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'artwork', 'added_on')
    search_fields = ('user__username', 'artwork__product_name')
    list_filter = ('added_on',)
    
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at')
    search_fields = ('user__username', 'message')
    
class QueryAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'category', 'query')
    search_fields = ('full_name', 'email', 'category', 'query')
    change_list_template = "admin/query/queries_change_list.html"  # Custom template for QueryAdmin

    def changelist_view(self, request, extra_context=None):
        # Define a fixed order for the categories
        fixed_category_order = [
            'artwork quality', 'bidding issues', 'technical support', 'feedback',
            'suggestions', 'shipping and delivery', 'refund and returns', 
            'seller queries', 'legal or policy concerns', 'AR and visualization'
        ]

        # Aggregate data for the bar chart
        categories_data = (
            Query.objects.values("category")
            .annotate(total=Count("id"))
            .order_by("category")  # Ensure the categories are fetched in alphabetical order
        )

        # Define a mapping of categories to specific colors
        category_colors = {
            'artwork quality': 'rgba(54, 162, 235, 0.6)',  # Blue
            'bidding issues': 'rgba(255, 99, 132, 0.6)',   # Red
            'technical support': 'rgba(75, 192, 192, 0.6)',    # Teal
            'feedback': 'rgba(255, 182, 193, 0.6)',  # Pink
            'suggestions': 'rgba(255, 205, 86, 0.6)',  # Yellow
            'shipping and delivery': 'rgba(153, 102, 255, 0.6)',  # Purple
            'refund and returns': 'rgba(255, 159, 64, 0.6)',  # Orange
            'seller queries': 'rgba(100, 181, 246, 0.6)',  # Light Blue
            'legal or policy concerns': 'rgba(204, 158, 218, 0.94)',  # Lavender
            'AR and visualization': 'rgba(144, 238, 144, 0.6)',  # Light Green
        }

        # Initialize the final data structure
        category_counts = {category: 0 for category in fixed_category_order}

        # Populate the category_counts dictionary with the actual query data
        for category_data in categories_data:
            category = category_data["category"]
            category_counts[category] = category_data["total"]

        # Prepare data for Chart.js (ensuring the fixed order)
        labels = fixed_category_order  # Fixed order of categories
        data = [category_counts[category] for category in fixed_category_order]

        # Assign colors dynamically based on category
        background_colors = [category_colors.get(category, 'rgba(201, 203, 207, 0.6)') for category in labels]  # Default to grey if category is not in the map
        border_colors = [color.replace('0.6', '1') for color in background_colors]  # Darker borders

        # Pass the data and colors to the template
        extra_context = extra_context or {}
        extra_context["chart_data"] = {
            "labels": labels,
            "data": data,
            "background_colors": background_colors,
            "border_colors": border_colors,
        }
        return super().changelist_view(request, extra_context=extra_context)


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('rating', 'feedback_text', 'submitted_at')
    search_fields = ('rating', 'feedback_text')
    change_list_template = "admin/feedback/feedback_change_list.html"

    def changelist_view(self, request, extra_context=None):
        # Filter only frontend-submitted feedback
        frontend_feedback = Feedback.objects.filter(source="frontend")
        
        # Aggregate sentiment data for frontend feedback
        sentiment_data = (
            frontend_feedback.filter(sentiment__isnull=False)
            .values("sentiment")
            .annotate(total=Count("id"))
        )

        # Count "Only Feedback" and "Only Star Rating" for frontend data
        only_feedback_count = frontend_feedback.filter(
        Q(rating="") & ~Q(feedback_text="")
        ).count()

        only_rating_count = frontend_feedback.filter(
        ~Q(rating="") & Q(feedback_text="")
        ).count()
        
        # print("Only Feedback Count:", only_feedback_count)
        # print("Only Rating Count:", only_rating_count)
        
        # Sentiment chart data
        sentiment_labels = ["Positive", "Negative", "Neutral"]
        sentiment_data_values = [
            next((item["total"] for item in sentiment_data if item["sentiment"] == "positive"), 0),
            next((item["total"] for item in sentiment_data if item["sentiment"] == "negative"), 0),
            next((item["total"] for item in sentiment_data if item["sentiment"] == "neutral"), 0),
        ]
        sentiment_colors = ["#4CAF50", "#F44336", "#FFC107"]

        # "Only Feedback" and "Only Star Rating" chart data
        feedback_labels = ["Only Feedback", "Only Star Rating"]
        feedback_data_values = [only_feedback_count, only_rating_count]
        feedback_colors = ["#2196F3", "#9C27B0"]

        # Pass the data to the template
        extra_context = extra_context or {}
        extra_context["sentiment_chart_data"] = {
            "labels": sentiment_labels,
            "data": sentiment_data_values,
            "background_colors": sentiment_colors,
        }
        extra_context["feedback_chart_data"] = {
            "labels": feedback_labels,
            "data": feedback_data_values,
            "background_colors": feedback_colors,
        }
        print(extra_context["feedback_chart_data"])

        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Query, QueryAdmin)