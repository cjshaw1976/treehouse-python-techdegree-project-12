from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from . import models

class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    bio = forms.Textarea(attrs={'cols': 80, 'rows': 20})
    avatar = forms.ImageField(required=False)

    class Meta:
        model = models.Profile
        fields = [
            'bio',
            'avatar',
        ]

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()

        username = self.cleaned_data.get('username')
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError(u'Username "%s" is already in use.' % username)

        email = self.cleaned_data.get('email')
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError(u'Email "%s" is already in use.' % email)

        return cleaned_data


class SubscriberForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    password1 = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control',
                                      'type':'password'})
    )
    password2 = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control',
                                      'type':'password'})
    )

    # make email unique
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("The email already taken.")
        return email


class CropForm(forms.Form):
    """ Hide a fields to hold the coordinates chosen by the user """
    scale = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'display:none'}))
    angle = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'display:none'}))
    x = forms.CharField(widget=forms.Textarea(attrs={'style': 'display:none'}))
    y = forms.CharField(widget=forms.Textarea(attrs={'style': 'display:none'}))
    w = forms.CharField(widget=forms.Textarea(attrs={'style': 'display:none'}))
    h = forms.CharField(widget=forms.Textarea(attrs={'style': 'display:none'}))
