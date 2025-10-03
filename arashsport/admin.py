from django.contrib import admin
from django.utils.html import format_html
from arashsport.models import Category, Vendor, Product, ProductImage, ProductReview, CartOrder, ItemOrder, UserWishList


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['cid', 'title']


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['vid', 'name', 'get_user_full_name', 'contact', 'verified', 'preview_image']
    raw_id_fields = ['user']
    list_editable = ['verified']

    def preview_image(self, obj):
        if obj.image:
            return format_html(f'<img src={obj.image.url} width="50" height="50"/>')

    def get_user_full_name(self, obj):
        if obj.user:
            return obj.user.get_full_name()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    def final_price(self, obj):
        if obj.off_price:
            return f'{obj.off_price:,}'
        return f'{obj.price:,}'
    def image_preview(self,obj):
        try:
            thumbnail_image = obj.images.all()[0]
            return format_html(f'<img src={thumbnail_image.image.url} width="50" height="50" />')
        except:
            thumbnail_image = None

    list_display = ['pid', 'name', 'image_preview','vendor__name', 'final_price', 'tags__title', 'status', 'in_stack',
                    'featured']
    raw_id_fields = ['vendor', 'tags']
    inlines = [ProductImageInline]
    list_editable = ['status', 'in_stack', 'featured']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'date']
    raw_id_fields = ['product']

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'date']
    raw_id_fields = ['user', 'product']

@admin.register(CartOrder)
class CartOrderAdmin(admin.ModelAdmin):
    list_display = ['id','date','is_paid','status']
@admin.register(ItemOrder)
class ItemOrderAdmin(admin.ModelAdmin):
    list_display = ['product__name','order__id','quantity','total_price']
@admin.register(UserWishList)
class UserWishListAdmin(admin.ModelAdmin):
    list_display = ['user__id','product__name','date']