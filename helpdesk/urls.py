from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from core.forms import LoginForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form=LoginForm,), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('api/', include('core.urls_api')),
    path('api-auth/', include('rest_framework.urls')),

    path('', include('core.urls')),
]

