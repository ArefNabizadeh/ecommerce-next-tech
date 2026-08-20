from django import forms
from .models import CartItem



class CartItemForm(forms.ModelForm):


    class Meta:
        model = CartItem
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'min': 1,
                'class': 'w-16 text-center rounded-xl border bg-white/50 px-2 py-1.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200'
            })
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise forms.ValidationError('تعداد باید حداقل ۱ باشد.')
        return quantity