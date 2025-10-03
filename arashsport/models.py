from django.db import models
from django.urls import reverse
from shortuuid.django_fields import ShortUUIDField
from user_auth.models import User
from ckeditor.fields import RichTextField


def vendor_image_path(instance, filename):
    return f'vendors/{instance.vid}/{filename}'


def product_image_path(instance, filename):
    return f'products/{instance.product.pid}/{filename}'


class Category(models.Model):
    cid = ShortUUIDField(unique=True, editable=False, length=12, prefix='cat_', verbose_name='شماره')
    title = models.CharField(max_length=100, verbose_name='عنوان')
    image = models.ImageField(upload_to='categories/', verbose_name='تصویر')

    class Meta:
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'


class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, editable=False, length=12, prefix='ven_', verbose_name='شماره')
    name = models.CharField(max_length=100, verbose_name='نام فروشگاه')
    description = RichTextField(verbose_name='توضیحات')
    image = models.ImageField(upload_to=vendor_image_path, verbose_name='تصویر')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendors', verbose_name='مسئول')
    address = models.TextField(verbose_name='آدرس')
    contact = models.CharField(max_length=100, verbose_name='شماره تماس')
    verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'فروشگاه'
        verbose_name_plural = 'فروشگاه ها'

    def save(self, *args, **kwargs):
        if self.id is None:
            temp_image = self.image
            self.image = None
            super().save(*args, **kwargs)
            self.image = temp_image
            self.save()
        else:
            old_instance = Vendor.objects.get(pk=self.pk)
            if old_instance.image and old_instance.image != self.image:
                old_instance.image.delete(save=False)
            super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('arashsport:vendor detail', args=[self.pk])


class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_image_path, verbose_name='تصویر')
    date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')

    class Meta:
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصاویر محصول'


class Product(models.Model):
    status_choices = (
        ('draft', 'در حال تکمیل'),
        ('rejected', 'حذف شده'),
        ('in review', 'در حال بررسی'),
        ('published', 'تایید شده')
    )
    pid = ShortUUIDField(unique=True, editable=False, length=12, prefix='p_', verbose_name='شماره')
    name = models.CharField(max_length=255, verbose_name='نام محصول')
    vendor = models.ForeignKey(Vendor, related_name='products', on_delete=models.CASCADE, verbose_name='فروشگاه')
    description = RichTextField(verbose_name='توضیحات')
    price = models.PositiveIntegerField(verbose_name='قیمت')
    off_price = models.PositiveIntegerField(null=True, blank=True, verbose_name='قیمت با تخفیف')
    tags = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products',
                             verbose_name='دسته بندی')
    status = models.CharField(max_length=10, choices=status_choices, default='in review', verbose_name='وضعیت کالا')
    stack_number = models.PositiveIntegerField(verbose_name='تعداد موجود در انبار')
    in_stack = models.BooleanField(default=False, verbose_name='موجود؟')
    featured = models.BooleanField(default=False, verbose_name='محصول ویژه؟')
    rate = models.DecimalField(max_digits=2, decimal_places=1, verbose_name='امتیاز', default=0.0)
    date = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'

    def calc_off_percentage(self):
        return f'{(self.price - self.off_price if self.off_price else 0) / self.price * 100:.1f}'

    def get_absolute_url(self):
        return reverse('arashsport:product detail', args=[self.id])


class ProductReview(models.Model):
    rate_choice = (
        (1, '۱'),
        (2, '۲'),
        (3, '۳'),
        (4, '۴'),
        (5, '۵'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name='کاربر')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews', verbose_name='محصول')
    date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')
    content = models.TextField(verbose_name='متن', blank=True, null=True)
    rate = models.IntegerField(choices=rate_choice, null=True, blank=True, verbose_name='نمره')

    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'


class UserWishList(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishes', verbose_name='محصول')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wish_list', verbose_name='کاربر')
    date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'فهرست آرزو'
        verbose_name_plural = 'فهرست آرزوها'




class CartOrder(models.Model):
    status_choice = (
        ('process', 'در حال انجام'),
        ('shipping', 'در حال ارسال'),
        ('delivered', 'تحویل داده شده')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='کاربر')
    total_price = models.PositiveIntegerField(verbose_name='مبلغ قابل پرداخت')
    date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')
    is_paid = models.BooleanField(default=False, verbose_name='پرداخت شده؟')
    status = models.CharField(choices=status_choice, max_length=50, verbose_name='وضعیت',default='process')

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش ها'


class ItemOrder(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE, related_name='items', verbose_name='سفارش')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items_order', verbose_name='کالا')
    quantity = models.PositiveSmallIntegerField(verbose_name='تعداد')
    total_price = models.PositiveIntegerField(verbose_name='قیمت نهایی')

    class Meta:
        verbose_name = 'کالا سفارش'
        verbose_name_plural = 'کالا های سفارش'
