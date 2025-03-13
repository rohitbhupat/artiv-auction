from django.urls import path,include
from art import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

app_name = "art"
urlpatterns = [
   path('',views.index.as_view(),name="index"),
   path('signup/',views.register_user,name="register_user"),
   path('register_seller/',views.RegisterSeller.as_view(),name="register_seller"),
   path('accounts/login/',views.user_login,name="login"),
   path('profile/',views.Profile.as_view(),name="profile"),
   path('logout/',views.logout_view,name="logout"),
   path('viewdetails/<int:pk>/',views.ArtworkDetailView.as_view(),name="product_details"),
   path('artwork-sale_details/<int:pk>/',views.ArtworkSaleDetailView.as_view(),name="artwork_sale_detail"),
   path('addorder/<int:pk>',views.OrderCreateView.as_view(),name="place_order"),
   path('sale-order/<int:pk>',views.SaleOrderCreateView.as_view(),name="sale_order"),
   path('orderconfirm/',views.OrderCreateView.as_view(),name="confirm_order"),
   path("callback/", views.callback, name="callback"),
   path("arview/<int:id>", views.ArView.as_view(), name="view_3d"),
   path('arview/update/', views.ArView.as_view(), name='arview-update'),
   # path('360view/<int:id>/', views.View360.as_view(), name='view360'),
   path("about/", views.About.as_view(), name="about"),
   path("contact/", views.Contact.as_view(), name="contact"),
   path("faq/", views.FAQs.as_view(), name="faq"),
   path("terms/", views.Terms.as_view(), name="terms"),
   path("privacy/", views.Privacy.as_view(), name="privacy"),
   path("purchase_cancel/", views.Purchase_Cancel.as_view(), name="purchase_cancel"),
   path("auction_cancel/", views.Auction_Cancel.as_view(), name="auction_cancel"),
   path('unsold/',views.UnsoldListView.as_view(),name="unsold_items"),
   path('artwork-sale/',views.ArtworkSaleListView.as_view(),name="artwork_sale"),
   path('cat/<int:id>/',views.CatListView.catalog_products,name="catalog_products"),
   path('purchase-cat/<int:id>/', views.PurchaseCategoryView.as_view(), name="purchase_category_products"),
   path('profile-settings/', views.profile_settings, name='profile_settings'),
   path('toggle_favorite/', views.toggle_favorite, name='toggle_favorite'),   
   path('favorites/', views.favorites_page, name='favorites_page'),
   path('get_favorites/', views.get_favorites, name='get_favorites'),
   path('remove-favorite/<int:artwork_id>/', views.remove_favorite, name='remove_favorite'),
]
if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)