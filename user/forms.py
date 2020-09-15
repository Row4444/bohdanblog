from django import forms
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import UserCreationForm
from django.template.loader import render_to_string

from user.models import User
from user.tasks import send_email_user
from user.tokens import signer


class DateInput(forms.DateInput):
    input_type = 'date'


class PasswordFirstForm(forms.Form):
    email = forms.EmailField(max_length=254, help_text='Add a valid email address.')
    email_template = "user/email/password_reset_email.html"

    class Meta:
        model = User
        fields = ('email',)

    def send_email(self, current_site):
        email = self.cleaned_data['email']
        username = self.cleaned_data.get('username', False)
        if not username:
            username = User.objects.get(email=email)
            message = self.make_message(username, current_site)
            send_email_user(email, message)

    def make_message(self, username, current_site):
        token = self.get_token(username)
        message = render_to_string(self.email_template, {
            'user': username,
            'domain': current_site,
            'token': token,
        })
        return message

    def get_token(self, username):
        token = signer.sign(username)
        return token

    def clean_username(self, token):
        username = signer.unsign(token)
        return username


class PasswordForgotForm(forms.Form):

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text="Enter the same password as before, for verification.",
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2


class RegistrationForm(PasswordFirstForm, UserCreationForm):
    email_template = 'user/email/email_template.html'

    email = forms.EmailField(max_length=254, help_text='Add a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'date_of_birth', 'password1', 'password2',)
        widgets = {'date_of_birth': DateInput()}


class AuthenticationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'password')

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        if not authenticate(username=username, password=password):
            raise forms.ValidationError('Invalid login')
