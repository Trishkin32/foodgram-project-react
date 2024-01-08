from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from foodgram_backend.settings import (HEX_LEN, MAX_COOKING_TIME,
                                       MAX_INGR_AMOUNT,
                                       MEASURE_UNIT_LEN, MIN_COOKING_TIME,
                                       MIN_INGR_AMOUNT, NAME_LEN, SLUG_LEN,
                                       TAG_LEN)
from users.models import User

from .validators import validate_hex


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        verbose_name='Название тега',
        unique=True,
        max_length=TAG_LEN,
    )
    color = models.CharField(
        verbose_name='Цвет тега',
        unique=True,
        max_length=HEX_LEN,
        validators=(validate_hex,),
    )
    slug = models.SlugField(
        verbose_name='Слаг тега',
        unique=True,
        max_length=SLUG_LEN,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=NAME_LEN,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MEASURE_UNIT_LEN,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=NAME_LEN,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                'Время приготовления должно быть больше или равно'
                f'{MIN_COOKING_TIME}.'
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                f'Время приготовления не может быть больше {MAX_COOKING_TIME}.'
            )
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации рецепта',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель связи моделей рецептов и ингредиентов."""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=[
            MinValueValidator(
                MIN_INGR_AMOUNT,
                f'Количество должно быть больше или равно{MIN_INGR_AMOUNT}.'
            ),
            MaxValueValidator(
                MAX_INGR_AMOUNT,
                f'Количество не может быть больше {MAX_INGR_AMOUNT}.'
            )
        ],
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='Ингредиенты уникальны.'
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name},'
            f'{self.amount}'
            f'{self.ingredient.measurement_unit}'
        )


class AbstractFavoriteCart(models.Model):
    """Абстрактная модель для избранного."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class Favorite(AbstractFavoriteCart):
    """Модель избранного для рецептов."""

    class Meta:
        ordering = ('user',)
        default_related_name = 'favorites'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='Рецепт уже в избранном.'
            ),
        )

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCart(AbstractFavoriteCart):
    """Модель списка покупок."""

    class Meta:
        ordering = ('user',)
        default_related_name = 'carts'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='Рецепт уже в корзине.'
            ),
        )

    def __str__(self):
        return f'{self.user.username} добавил в корзину {self.recipe.name}'
