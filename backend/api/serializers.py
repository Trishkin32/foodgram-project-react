from django.conf import settings
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import Follow, User
from users.validators import validate_username

from .utils import Base64ImageField


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_is_subscribed',
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        follower = self.context['request'].user
        if follower.is_anonymous:
            return False
        return Follow.objects.filter(
            user=follower,
            following=obj
        ).exists()


class UserRegistrationSerializer(UserSerializer):
    """Сериализатор регистрации пользователя."""

    first_name = serializers.CharField(
        required=True,
        max_length=settings.FIRST_NAME_LEN,
    )
    last_name = serializers.CharField(
        required=True,
        max_length=settings.LAST_NAME_LEN,
    )
    username = serializers.CharField(
        required=True,
        max_length=settings.USERNAME_LEN,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            validate_username
        ],
    )
    email = serializers.EmailField(
        required=True,
        max_length=settings.EMAIL_LEN,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
    )
    password = serializers.CharField(
        required=True,
        max_length=settings.PASSWORD_LEN,
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для входа."""

    password = serializers.CharField(
        max_length=settings.PASSWORD_LEN,
    )
    email = serializers.EmailField(
        max_length=settings.EMAIL_LEN,
    )


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор изменения пароля."""

    new_password = serializers.CharField(
        required=True,
        max_length=settings.PASSWORD_LEN,
    )
    current_password = serializers.CharField(
        required=True,
        max_length=settings.PASSWORD_LEN,
    )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        read_only_fields = fields


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения модели рецепт-ингредиент."""

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True,
    )
    name = serializers.CharField(
        source='ingredient.name',
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )
        read_only_fields = fields


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания модели рецепт-ингредиент."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )
    amount = serializers.IntegerField(
        min_value=settings.MIN_INGR_AMOUNT,
        max_value=settings.MAX_INGR_AMOUNT
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""

    tags = TagSerializer(many=True,)
    author = UserSerializer()
    image = Base64ImageField()
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        source='recipe_ingredients',
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited',
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = fields

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.carts.filter(recipe=obj).exists()
        )


class RecipeInListSerializer(serializers.ModelSerializer):
    """Сериализатор с кратким отображением рецепта."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = fields


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = RecipeIngredientWriteSerializer(
        many=True,
        source='recipe_ingredients',
    )
    text = serializers.CharField(
        required=True,
    )
    cooking_time = serializers.IntegerField(
        max_value=settings.MAX_COOKING_TIME,
        min_value=settings.MIN_COOKING_TIME,
        required=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Ингредиенты должны быть заданы.'
            )
        ingredient_tuples = [
            (ingredient['ingredient'],
             ingredient['amount'])
            for ingredient in ingredients
        ]

        if len(set(ingredient_tuples)) != len(ingredients):
            raise serializers.ValidationError(
                'Такой ингредиент уже в рецепте.'
            )

        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Теги должны быть заданы.'
            )
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                'Такой тег уже в рецепте.'
            )

        return tags

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                'Поле изображения не может быть пустым.'
            )
        return image

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredients.sort(
            key=lambda ingredient: ingredient.get('ingredient').name
        )
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient.get('ingredient').id,
                    amount=ingredient.get('amount')
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):

        if 'tags' not in validated_data:
            instance.tags.clear()
            instance.tags.set(validated_data.pop('tags'))

        if 'recipe_ingredients' not in validated_data:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            ingredients = validated_data.pop('recipe_ingredients')
            self.create_ingredients(instance, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    email = serializers.ReadOnlyField(source='following.email')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes',
    )
    recipes_count = serializers.ReadOnlyField(source='following.recipes.count')

    class Meta:
        model = Follow
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = fields

    def get_recipes(self, following):
        request = self.context.get('request')
        recipes_limit = int(
            request.query_params['recipes_limit']
            or 0
        )
        recipes = Recipe.objects.filter(
            author=following.following
        )[:recipes_limit]
        serializer = RecipeInListSerializer(
            recipes,
            many=True,
            read_only=True,
            context={'request': request}
        )

        return serializer.data
