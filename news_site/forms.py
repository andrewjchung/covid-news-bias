from django import forms
from .models import Article

class SearchForm(forms.ModelForm):
    """Used to search for pandemics."""

    class Meta:
        model = Article 
        fields = ['disease']
