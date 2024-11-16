from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category  # The model the form is based on
        fields = ['name', 'description']  # Fields to include in the form
