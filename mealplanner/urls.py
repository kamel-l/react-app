

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import  weekly_meal_planner


urlpatterns = [
    path('mealplanner/', weekly_meal_planner, name='mealplanner'),
    path('add_meal/', views.add_meal, name='add_meal'),
    path('delete_meal/<int:id>/', views.delete_meal, name='delete_meal'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


