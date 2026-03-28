from django.urls import path
from .views import ProductListView, ProductDetailView, OrderListView, VendorInventoryView, VendorOrderListView, VendorAnalyticsView

urlpatterns = [
    path('vendor/analytics/', VendorAnalyticsView.as_view(), name='vendor-analytics'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/manage/', VendorInventoryView.as_view(), name='vendor-inventory'),
    path('products/manage/<str:product_id>/', VendorInventoryView.as_view(), name='vendor-item-manage'),
    path('vendor/orders/', VendorOrderListView.as_view(), name='vendor-orders'),
    path('vendor/orders/<str:order_id>/', VendorOrderListView.as_view(), name='vendor-order-detail'),
    path('products/<str:product_id>/', ProductDetailView.as_view(), name='product-detail'),
    path('orders/', OrderListView.as_view(), name='order-list'),
]
