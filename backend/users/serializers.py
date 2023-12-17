from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Recipe
from users.models import Follow

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""
    class Meta:
        model = User
        fields = (
            (User.USERNAME_FIELD, "password", "id",)
            + tuple(User.REQUIRED_FIELDS)
        )


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            (User.USERNAME_FIELD, "id",)
            + tuple(User.REQUIRED_FIELDS)
            + ("is_subscribed",)
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request.user.is_authenticated:
            return False
        return Follow.objects.filter(
            user=request.user,
            author=obj,
        ).exists()


class RecipeUserSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта пользователя."""

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class SubscriptionSerializer(UserSerializer):
    """Сериализатор подписчик пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        recipes_limit = self.context["request"].query_params.get(
            "recipes_limit"
        )
        recipes = obj.recipes.all()
        if recipes_limit:
            limit = int(recipes_limit)
            recipes = recipes[:limit]
        return RecipeUserSerializer(recipes, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def to_representation(self, instance):
        data = super(UserSerializer, self).to_representation(instance)
        return data
