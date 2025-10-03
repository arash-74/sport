from django import forms

from arashsport.models import ProductReview


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['content', 'rate']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['rate'] or cleaned_data['content'] != '':
            return cleaned_data
        else:
            raise forms.ValidationError('حداقل یکی از فیلد های امتیاز یا متن باید پر شود')