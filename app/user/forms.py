from django import forms
from django.contrib.auth import get_user_model


class LoginForm(forms.Form):
    email = forms.CharField(label='Email', error_messages={
        'required': 'Email must not be empty'})
    password = forms.CharField(label='Password', widget=forms.PasswordInput(),
                               error_messages={'required': 'Password must not'
                                                           'be empty'})
