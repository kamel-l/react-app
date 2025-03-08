from django.db.models import Q
from recipe.models import Recipe, Cat

class RecipeService:
    @staticmethod
    def get_recipe(recipe_id):
        try:
            return Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            return None

    @staticmethod
    def get_all_recipes():
        return Recipe.objects.all().select_related('user')

    @staticmethod
    def get_all_recipes_with_filters(filters):
        queryset = Recipe.objects.all().select_related('user')
        
        if filters.get('category'):
            queryset = queryset.filter(category=filters['category'])
            
        if filters.get('search'):
            queryset = queryset.filter(
                Q(name__icontains=filters['search']) |
                Q(description__icontains=filters['search'])
            )
            
        return queryset.order_by('-created_at')

    @staticmethod
    def create_recipe(data, user):
        try:
            recipe = Recipe.objects.create(
                name=data['name'],
                description=data['description'],
                preparation_time=data['preparation_time'],
                cooking_time=data['cooking_time'],
                servings=data['servings'],
                instructions=data['instructions'],
                category_id=data.get('category'),
                user=user
            )
            return recipe
        except Exception as e:
            raise ValueError(f"Error creating recipe: {str(e)}")

    @staticmethod
    def update_recipe(recipe_id, data):
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            for key, value in data.items():
                if hasattr(recipe, key):
                    setattr(recipe, key, value)
            recipe.save()
            return recipe
        except Recipe.DoesNotExist:
            raise ValueError("Recipe not found")

    @staticmethod
    def delete_recipe(recipe_id):
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            recipe.delete()
            return True
        except Recipe.DoesNotExist:
            return False

    @staticmethod
    def get_user_recipes(user):
        return Recipe.objects.filter(user=user)

    @staticmethod
    def get_categories():
        return Category.objects.all()

    @staticmethod
    def search_recipes(query):
        return Recipe.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).select_related('user')