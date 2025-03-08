

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('shopping/', views.shopping, name='shopping'),
    # Nouvelles URLs pour la gestion de la liste de courses
    path('add_shopping_item/', views.add_custom_item, name='add_custom_item'),
    path('shopping/sync-with-planning/', views.sync_with_planning, name='sync_with_planning'),
    path('shopping/clear-list/', views.clear_shopping_list, name='clear_shopping_list'),
    path('delete_shopping_item/<int:item_id>/', views.delete_shopping_item, name='delete_shopping_item'),
    path('shopping/update-item/<int:item_id>/', views.update_shopping_item, name='update_shopping_item'),
    # URL optionnelle pour exporter la liste
    path('shopping/export/', views.export_shopping_list, name='export_shopping_list'),
    
    
   
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


