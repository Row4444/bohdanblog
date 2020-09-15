from django.contrib.auth import logout, authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import FormView, CreateView, DetailView, UpdateView

from user.forms import RegistrationForm, AuthenticationForm, DateInput, PasswordFirstForm, PasswordForgotForm
from user.models import User
from user.tokens import signer
from user.utils import ModelFormWidgetMixin


class RegisterView(CreateView):
    template_name = 'user/account_data.html'
    form_class = RegistrationForm
    success_url = '/articles/'
    context_dict = {'title': 'Registration', 'button': 'Registration'}

    def get_context_data(self, **kwargs):
        context = super(RegisterView, self).get_context_data(**kwargs)
        context.update(self.context_dict)
        return context

    def form_valid(self, form):
        valid = super(RegisterView, self).form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        if new_user:  # Дэн = Свэн
            login(self.request, new_user)
            current_site = get_current_site(self.request).domain
            form.send_email(current_site)
        return valid


class ForgotPasswordView(FormView):
    template_name = 'user/account_data.html'
    form_class = PasswordFirstForm
    success_url = '/articles/'
    context_dict = {'title': 'Forgot password', 'button': 'Send email'}

    def get_context_data(self, **kwargs):
        context = super(ForgotPasswordView, self).get_context_data(**kwargs)
        context.update(self.context_dict)
        return context

    def form_valid(self, form):
        valid = super(ForgotPasswordView, self).form_valid(form)
        try:
            User.objects.get(email=form.cleaned_data['email'])
            current_site = get_current_site(self.request).domain
            form.send_email(current_site)
            messages.success(self.request, 'Check your email box.')
        except User.DoesNotExist:
            messages.error(self.request, 'Anyone user have this e-mail')
            return redirect('forgot_password')
        return valid


class ResetPasswordView(View):
    def get(self, request, token):
        username = signer.unsign(token)
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, r"Don't play with my site!")
            return redirect('all')
        form = PasswordForgotForm()
        return render(request, 'user/account_data.html',
                      {'title': '{}. Create a new password'.format(username), 'button': 'Reset', 'form': form})

    def post(self, request, token):
        if request.method == 'POST':
            form = PasswordForgotForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data.get('password1', False)
                if password:
                    username = signer.unsign(token)
                    user = User.objects.get(username=username)
                    new_password = form.cleaned_data.get('password1')
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Done! Try to LogIn now.')
            else:
                messages.error(request, form.errors)
                return redirect('reset_password', token)
            return redirect('authentication')


class ChangePasswordView(View):
    def get(self, request):
        form = PasswordChangeForm(user=request.user)
        return render(request, 'user/account_data.html',
                      {'title': 'Change Password', 'button': 'Change', 'form': form})

    def post(self, request):
        if request.method == 'POST':
            if request.user.is_authenticated:
                form = PasswordChangeForm(data=request.POST, user=request.user)
                if form.is_valid():
                    user = form.save()
                    messages.success(request, 'New password changed. LogIn please.')
                    update_session_auth_hash(request, user)
                    return redirect('authentication')
                else:
                    messages.error(request, form.errors)
            else:
                messages.error(request, 'Must be LogIn!')
            return redirect('change_password')


class AccountDetailView(ModelFormWidgetMixin, UpdateView):
    model = User
    fields = ['username', 'date_of_birth']
    widgets = {'date_of_birth': DateInput()}
    template_name = 'user/account_data.html'
    success_url = '/update/'
    context_dict = {'title': 'Update Account', 'button': 'Update'}

    def get_context_data(self, **kwargs):
        context = super(AccountDetailView, self).get_context_data(**kwargs)
        context.update(self.context_dict)
        return context

    def form_valid(self, form):
        valid = super(AccountDetailView, self).form_valid(form)
        messages.success(self.request, 'Your profile was updated.')
        return valid

    def get_object(self, queryset=None):
        return self.request.user


class AuthenticationView(FormView):
    template_name = 'user/account_data.html'
    form_class = AuthenticationForm
    success_url = '/articles/'
    context_dict = {'title': 'Login', 'button': 'Login'}

    def get_context_data(self, **kwargs):
        context = super(AuthenticationView, self).get_context_data(**kwargs)
        context.update(self.context_dict)
        return context

    def form_valid(self, form):
        return super(AuthenticationView, self).form_valid(form)

    def get_initial(self):
        initial = super(AuthenticationView, self).get_initial()
        username = self.request.POST.get('username', False)
        password = self.request.POST.get('password', False)
        user = authenticate(username=username, password=password)
        if user:
            login(self.request, user)
        return initial


def activate(request, token):
    token_uncode = signer.unsign(token)
    try:
        user = User.objects.get(username=token_uncode)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None:
        user.is_verify = True
        user.save()
        messages.success(request, 'Your account is verify now! Welcome!')
    return redirect('all')


def logout_view(request):
    logout(request)
    return redirect('authentication')
