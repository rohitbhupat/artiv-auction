from django.urls import path
from dashboard import views
from django.conf import settings  # Correct import
from django.conf.urls.static import static

app_name = "dashboard"
urlpatterns = [
    path('addproduct/', views.ArtworkCreateView.as_view(), name="add_product"),
    path('product/', views.ArtworkListView.as_view(), name="product_list"),
    path('bidlist/', views.BidListView.as_view(), name="bid_list"),
    path('productupdate/<int:pk>/', views.ArtworkUpdateView.as_view(), name="product_update"),
    path('product/<int:pk>/delete/', views.ArtworkDeleteView.as_view(), name="product_delete"),
    path('order/', views.OrderListView.as_view(), name="order_list"),
    path('placebid/', views.BidCreateView.as_view(), name="place_bid"),
    path('latest_bid/<int:pk>/', views.latest_bid, name='latest_bid'),
    path('fetch_notifications/', views.fetch_notifications, name='fetch_notifications'),
    path('notifications/mark_as_read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('dismiss_notification/<int:notification_id>/', views.dismiss_notification, name='dismiss_notification'),
    path('clear_all_notifications/', views.clear_all_notifications, name='clear_all_notifications'),
    path('submit_query/', views.SubmitQueryView.as_view(), name='submit_query'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('contact/', views.SubmitQueryView.as_view(), name='contact'),
    # path('check_auction_status/', views.check_auction_status, name='check_auction_status'),
    path('confirm_purchase/<int:artwork_id>/', views.confirm_purchase, name='confirm_purchase'),
    path('get_shipping_status/<int:order_id>/', views.get_shipping_status, name='get_shipping_status'),
    path('update_shipping_status/', views.update_shipping_status, name='update_shipping_status'),
    path('cancel_order/', views.cancel_order, name='cancel_order'),
    path('autocomplete/', views.autocomplete_artworks, name='autocomplete_artworks'),
    path('get_artworks_json/', views.get_artworks_json, name='get_artworks_json'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
