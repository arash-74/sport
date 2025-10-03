from django.db.models import Avg
from django.template import Library

from arashsport.models import Vendor

register = Library()


@register.filter()
def price_handler(value):
    return f'{value:,}'


@register.filter()
def off_handler(obj):
    return f'{obj.off_price / obj.price * 100}%'


@register.filter()
def calc_vendor_rate(vid):
    print(vid)
    # return ''
    rate = Vendor.objects.get(vid=vid).products.annotate(avg=Avg('rate')).values('avg')[0]['avg']
    return f'{rate:.1f}'


@register.filter()
def truncate(text, number):
    text = text.split(' ')
    return ' '.join(text[:number])
