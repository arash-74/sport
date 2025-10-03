from django.core.exceptions import ValidationError
from django.db.models import Avg
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save, pre_save
from arashsport.models import ProductReview
from arashsport.models import Product


@receiver(post_save, sender=ProductReview)
def calc_product_rate(sender, instance, **kwargs):
    instance.product.rate = instance.product.reviews.aggregate(avg=Avg('rate'))['avg']
    instance.product.save()


@receiver(pre_save, sender=ProductReview)
def check_one_field_fill(sender, instance, **kwargs):
    if instance.rate is None and instance.content == '':
        raise ValidationError('حداقل یکی از فیلد های rate یا content باید پر شود')


@receiver(pre_save, sender=ProductReview)
def check_person_rate_one(sender, instance, **kwargs):
    if not instance.id or (instance.id and instance.rate != ProductReview.objects.get(id=instance.id).rate):
        exist_rows = ProductReview.objects.filter(product=instance.product, user=instance.user).exclude(
            id=instance.id if instance.id else None)
        if exist_rows.exists() and any([review.rate for review in exist_rows]):
            raise ValidationError('هر کاربر تنها یکبار می تواند امتیاز بدهد')
