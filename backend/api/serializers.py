from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingList, Tag)
from users.serializers import SubscriptionSerializer

from .utils import Base64ImageField


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientForRecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов для рецепта."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "amount")


class IngredientInRecipeSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(
        source="ingredient.name",
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit",
        read_only=True,
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount"
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()
    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    author = SubscriptionSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source="ingredientinrecipe_set",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return ShoppingList.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def validate(self, data):
        ingredients = self.initial_data.get("ingredients")
        tags = self.initial_data.get("tag")
        if not tags:
            raise serializers.ValidationError(
                {"tags": "Нет выбранных тегов"}
            )
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Нет выбранных ингредиентов"}
            )
        if len(tags) > len(set(tags)):
            raise serializers.ValidationError(
                "Теги не должны повторяться"
            )
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_item["id"]
            )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    "Данный ингредиент уже есть в списке"
                )
            ingredient_list.append(ingredient)
            if int(ingredient_item["amount"]) < 0:
                raise serializers.ValidationError(
                    {"ingredients": ("Данное значение недопустимо")}
                )
        data["ingredients"] = ingredients
        print(ingredients)
        return data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get("id"),
                amount=ingredient.get("amount"),
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = self.initial_data.get("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, sample, validated_data):
        sample.image = validated_data.get("image", sample.image)
        sample.name = validated_data.get("name", sample.name)
        sample.text = validated_data.get("text", sample.text)
        sample.cooking_time = validated_data.get(
            "cooking_time", sample.cooking_time
        )
        sample.tags.clear()
        tags_data = self.initial_data.get("tags")
        sample.tags.set(tags_data)
        IngredientInRecipe.objects.filter(recipe=sample).delete()
        self.create_ingredients(validated_data.get("ingredients"), sample)
        sample.save()
        return sample


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избанных рецептов."""

    id = serializers.IntegerField(source="recipe.id")
    name = serializers.CharField(source="recipe.name")
    image = serializers.ImageField(source="recipe.image")
    cooking_time = serializers.IntegerField(source="recipe.cooking_time")

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
