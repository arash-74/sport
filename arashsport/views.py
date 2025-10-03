import json
from operator import itemgetter

from django.contrib import messages
from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import Paginator, PageNotAnInteger
from django.db.models import Min, Max
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404

from arashsport.cart import Cart
from arashsport.forms import ProductReviewForm
from arashsport.models import Product, Vendor, ProductReview, CartOrder, ItemOrder, UserWishList


# Create your views here.
def home_view(request):
    products = Product.objects.all().order_by('-date')[:4]
    featured_products = Product.objects.all().filter(featured=True).order_by('-date')
    context = {'products': products, 'featured_products': featured_products}
    return render(request, 'html/arashsport/home.html', context)


def products_list_view(request):
    category = request.GET.get('category')
    order = request.GET.get('order')
    search = request.GET.get('search')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    products = Product.objects.all().order_by('-date')
    if category:
        products = products.filter(tags__title=category)
    if order:
        if order == 'ارزان ترین':
            products = products.order_by('price')
        if order == 'گران ترین':
            products = products.order_by('-price')
    if search:
        products = products.annotate(sim=TrigramSimilarity('name', search)).filter(sim__gt=0.1)
    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)
    products_min_price, products_max_price = itemgetter('min_price', 'max_price')(
        products.aggregate(min_price=Min('price'), max_price=Max('price')))
    pagination = Paginator(products, 4)
    products = pagination.page(request.GET.get('page', 1))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # from pdb import set_trace
        # set_trace()
        data = [{
            'product_get_absolute_url': product.get_absolute_url(),
            'product_rate': product.rate,
            'product_off': product.off_price,
            'product_off_perc': product.calc_off_percentage(),
            'image_url': product.images.first().image.url,
            'product_name': product.name,
            'product_vendor_name': product.vendor.name,
            'product_price': product.price,
        } for product in products.object_list]
        return JsonResponse({'status': 'ok', 'item': data, 'has_next': products.has_next()})
    featured_products = Product.objects.all().filter(featured=True).order_by('-date')
    context = {'products': products, 'featured_products': featured_products, 'category': category, 'order': order,
               'min': products_min_price, 'max': products_max_price, 'price_filter': 'true'}
    return render(request, 'html/arashsport/product_list.html', context)


def vendors_list_view(request):
    vendors = Vendor.objects.all().order_by('-id')
    context = {'vendors': vendors}
    return render(request, 'html/arashsport/vendor_list.html', context)


def vendor_detail_view(request, pk):
    vendor = Vendor.objects.get(pk=pk)
    context = {'vendor': vendor}
    return render(request, 'html/arashsport/vendor_detail.html', context)


def product_detail_view(request, pk):
    product = Product.objects.get(pk=pk)
    vendor = product.vendor
    wish_status = UserWishList.objects.filter(product=product, user=request.user).exists()
    comments_list = product.reviews.all().exclude(content='').exclude(content__isnull=True).order_by('-date')
    similar_products = Product.objects.filter(tags=product.tags).exclude(id=product.id)
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
    if request.method == 'GET':
        form = ProductReviewForm()
    context = {'product': product, 'vendor': vendor, 'comments_list': comments_list,
               'similar_products': similar_products, 'form': form, 'wish_status': wish_status}
    cart = Cart(request)
    return render(request, 'html/arashsport/product_detail.html', context)


def ajax_add_review(request, product_id):
    form = ProductReviewForm(request.POST)
    if form.is_valid():
        product = get_object_or_404(Product, pk=product_id)
        review = ProductReview.objects.create(
            product=product, user=request.user,
            rate=request.POST['rate'] if request.POST['rate'] != '' else None,
            content=request.POST['content']
        )
        count = product.reviews.all().exclude(content='').exclude(content__isnull=True).count()
        return JsonResponse({'status': 'ok', 'msg': 'با موفقیت ثبت شد', 'counter': count})
    else:
        return JsonResponse(
            {'status': 'error', 'msg': [b.message for val in form.errors.as_data().values() for b in val][0]})
    # request.


def ajax_add_to_cart(request):
    product_id = str(json.loads(request.body)['product_id'])
    qty = int(json.loads(request.body)['quantity'])
    product = get_object_or_404(Product, pk=product_id)
    cart = Cart(request)
    if product.stack_number < qty:
        return JsonResponse({'status': 'error', 'msg': 'مقدار مورد نظر در انبار موجود نمی باشد'})
    if cart.add(product_id, qty):
        data = [{
            'name': ' '.join(item['product'].name.split(' ')[:2]),
            'image': item['product'].images.first().image.url,
            'qty': item['qty'],
            'price': item['product'].off_price if item['product'].off_price else item['product'].price,
        } for item in cart.cart_to_product()]

        return JsonResponse({'status': 'ok', 'msg': 'محصول به سبد خرید اضافه شد', 'items': data})
    else:
        return JsonResponse({'status': 'error', 'msg': 'مقدار محصول انتخابی بیشتر از موجودی نمی تواند باشد'})


def cart_list_view(request):
    cart = Cart(request)
    total_price, price_sum = cart.cal_total_price()
    off_price = price_sum - total_price

    address = request.user.address
    phone = request.user.phone

    context = {
        'total_price': total_price,
        'price_sum': price_sum,
        'off_price': off_price,
        'address': address,
        'phone': phone
    }
    return render(request, 'html/arashsport/cart_list.html', context)


def ajax_del_from_cart(request):
    cart = Cart(request)
    id = json.loads(request.body)['id']
    # id = request.POST['id']
    if cart.delete(id):
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'error'})


def pay_bank_view(request):
    pay_status = True
    context = {}
    cart = Cart(request)
    total_price, price_sum = cart.cal_total_price()
    order = CartOrder.objects.create(user=request.user, total_price=total_price)
    if pay_status:
        for item in cart.cart_to_product():
            ItemOrder.objects.create(product=item['product'], order=order, quantity=item['qty'],
                                     total_price=item['total_price'])
            item['product'].stack_number -= item['qty']
            item['product'].save()
        order.is_paid = True
        order.save()
        context = {'cart_to_product': cart.cart_to_product()}
        cart.erase_cart()
    context['status'] = pay_status
    return render(request, 'html/arashsport/paybank.html', context)


def ajax_wish_handler(request, id):
    try:
        status = request.POST['status']
        print(status)
        if status == 'fa-regular':
            UserWishList.objects.create(user=request.user, product=Product.objects.get(id=id))
            return JsonResponse({'status': 'ok', 'msg':'به لیست علاقه مندی ها اضافه شد','icon_status':'fa-solid'})
        if status == 'fa-solid':
            UserWishList.objects.get(user=request.user, product=Product.objects.get(id=id)).delete()
            return JsonResponse({'status': 'ok', 'msg': 'از لیست علاقه مندی ها حذف شد','icon_status':'fa-regular'})

    except:
        return JsonResponse({'status': 'error', 'msg': 'خطایی رخ داده است'})
