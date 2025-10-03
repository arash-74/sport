from arashsport.cart import Cart
from arashsport.models import Category

def context_processor(request):
    return {'categories': Category.objects.all(),'cart':Cart(request)}