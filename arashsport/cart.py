from django.contrib.sites import requests
from django.db.models import Sum

from arashsport.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        if self.session.get('cart') is None:
            self.session['cart'] = {}
        self.cart = self.session['cart']

    def save(self):
        self.session.modified = True

    def add(self, product_id, qty):
        if self.cart.get(product_id):
            if self.cart.get(product_id)['quantity'] + qty <= Product.objects.get(id=product_id).stack_number:
                self.cart[product_id]['quantity'] += qty
            else:
                return False
        else:
            self.cart[product_id] = {'quantity': qty}
            print(self.cart)
        self.save()
        return True

    def cart_to_product(self):
        result = []
        for item in self.cart.keys():
            product = Product.objects.get(pk=item)
            price = product.off_price if product.off_price else product.price
            data = {
                'product': product,
                'qty': self.cart[item]['quantity'],
                'total_price': self.cart[item]['quantity'] * price
            }
            result.append(data)
        return result

    def delete(self, product_id):
        if self.cart.get(product_id):
            del self.cart[product_id]
            self.save()
            return True
        else:
            return False

    def erase_cart(self):
        self.cart.clear()
        self.save()

    def cal_total_price(self):
        total_price = 0
        price_sum = 0
        for item in self.cart_to_product():
            price = item['product'].off_price if item['product'].off_price else item['product'].price
            total_price += price * item['qty']
            price_sum += item['product'].price * item['qty']

        return total_price, price_sum

    def del_cart(self, id):
        if id in self.cart:
            del self.cart[id]
            self.save()
            return True
        else:
            return False
