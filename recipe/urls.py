

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import  comment_detail,user_recipe_comments,  unread_comments_count, mark_all_notifications_as_read, RecipeDetailView , delete_recipe, Sherche_recipes, recipe_generator, RecipesListsViews, notifications, mark_notification_as_read


urlpatterns = [
    path('', views.home, name='home'),
    path('recipe/new/', views.new_recipe, name='new_recipe'),
    path('RecipeDetailView/<int:recipe_id>/', views.RecipeDetailView, name='RecipeDetailView'),
    path('recipe/delete/<int:id>/', delete_recipe, name='delete_recipe'),
    path('sherche_recipes/', views.Sherche_recipes, name='Sherche_recipes'),
    path('generator/', views.recipe_generator, name='recipe_generator'),
    path('recipe/edit/<int:recipe_id>/', views.edit_recipe, name='edit_recipe'),
    path('recipe/<int:recipe_id>/update-image/', views.update_recipe_image, name='update_recipe_image'),
    path('my_recipes/', views.my_recipes, name='my_recipes'),
    path('RecipesListsViews/', RecipesListsViews.as_view(), name='RecipesListsViews'),
    path('view_recipe/<int:recipe_id>/', views.new_recipe, name='view_recipe'),
    path('recipe/<int:recipe_id>/review/', views.add_review, name='add_review'),
    path('find-recipes/', views.find_recipes_by_ingredients, name='find_recipes_by_ingredients'),
    path('recipe_search/', views.ingredient_sherch, name='recipe_search'),
    path('recipe/<int:recipe_id>/', views.recipe_detail_view, name='recipe_detail'),
    path('notifications/', notifications, name='notifications'),
    path('recipe/<int:recipe_id>/comment/<int:comment_id>/', comment_detail, name='comment_detail'),
    path('notifications/comment/<int:notification_id>/', views.view_comment, name='view_comment'),
    path('notifications/mark-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
    path('api/unread-comments-count/', unread_comments_count, name='unread_comments_count'),
     path('api/user-recipe-comments/', user_recipe_comments, name='user_recipe_comments'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


