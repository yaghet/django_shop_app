from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(min_length=5, max_length=30)
    password = forms.CharField(widget=forms.PasswordInput)
