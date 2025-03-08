from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('user_signup/', views.user_signup, name='user_signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='own_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile_view'),

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
