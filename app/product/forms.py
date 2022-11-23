from django import forms


class ProductSearchForm(forms.Form):
    search_phrase = forms.CharField(
        label='Product search phrase', max_length=200,
        error_messages={'required': 'Search phrase cannot be empty',
                        'max_length': 'Please enter shorter phrase'})


