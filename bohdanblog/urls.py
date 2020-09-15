from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from bohdanblog.views import first_screen
from user.views import AuthenticationView, logout_view, activate, RegisterView, AccountDetailView, ResetPasswordView, \
    ChangePasswordView, ForgotPasswordView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', first_screen),
    path('articles/', include('blog.urls')),
    path('registration/', RegisterView.as_view(), name='registration'),
    path('update/', AccountDetailView.as_view(), name='update'),
    path('authentication/', AuthenticationView.as_view(), name='authentication'),
    path('logout/', logout_view, name='logout'),
    path('activate/<token>/', activate, name='activate'),
    path('forgot/password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('account/password/change/', ChangePasswordView.as_view(), name='change_password'),
    path('reset/password/<token>', ResetPasswordView.as_view(), name='reset_password'),
    path('ckeditor/', include('ckeditor_uploader.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
