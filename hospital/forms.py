from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User

from .models import Patient, User
# Create a custom form that inherits from user form (reason --> for modify and customize)


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # password1 and password2 are required fields (django default)
        fields = ['username', 'email', 'password1', 'password2']
        # labels = {
        #     'first_name': 'Name',
        # }

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control floating'})


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'phone_number', 'blood_group',
                  'featured_image', 'history', 'nid', 'dob', 'address']


    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class PasswordResetForm(ModelForm):
    class Meta:
        model = User
        fields = ['email',"username"]

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control floating'})