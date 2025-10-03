from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from arashsport import views

app_name = 'arashsport'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products-list', views.products_list_view, name='product list'),
    path('vendors-list', views.vendors_list_view, name='vendor list'),
    path('vendor-detail/<int:pk>', views.vendor_detail_view, name='vendor detail'),
    path('product-detail/<int:pk>', views.product_detail_view, name='product detail'),
    path('add-review/<int:product_id>', csrf_exempt(views.ajax_add_review), name='add review'),
    path('add-cart',csrf_exempt(views.ajax_add_to_cart), name='add cart'),
    path('del-cart',csrf_exempt(views.ajax_del_from_cart), name='del cart'),
    path('wish/<int:id>',csrf_exempt(views.ajax_wish_handler),name='wish'),
    path('cart',views.cart_list_view, name='cart list'),
    path('pay',views.pay_bank_view,name='pay'),
]