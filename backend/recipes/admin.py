from django.contrib import admin

from .models import (Tag, Ingredient, Recipe, IngredientInRecipe,
                     Favorite, ShoppingList)


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Favorite)
admin.site.register(ShoppingList)


class IngredientInRecipeInline(admin.StackedInline):
    model = IngredientInRecipe


class RecipeAdmin(admin.ModelAdmin):
    list_filter = ("name", "author", "tags")
    inlines = [
        IngredientInRecipeInline,
    ]


admin.site.register(Recipe, RecipeAdmin)
