from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель тег."""

    name = models.CharField(
        max_length=200,
        verbose_name="Название"
    )
    color = models.CharField(
        max_length=50,
        verbose_name="Цвет"
    )
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("slug",)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингрединта."""

    name = models.CharField(
        max_length=255,
        verbose_name="Ингредиент"
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта"
    )
    name = models.CharField(
        verbose_name="Название",
        max_length=200
    )
    image = models.ImageField(
        upload_to="images",
        verbose_name="Картинка"
    )
    text = models.TextField(
        verbose_name="Описание"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientInRecipe",
        verbose_name="Ингредиенты",
        blank=True,
        related_name="recipes"
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Теги"
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Время приготовления в мин"
    )
    pub_date = models.DateField(
        verbose_name="Дата публикации",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-id",)

    def __str__(self):
        return self.name


class ShoppingList(models.Model):
    """Модель корзины покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепты"
    )

    class Meta:
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзина покупок"
        unique_together = ("user", "recipe")
        default_related_name = "shopping_list"

    def __str__(self):
        return f"{self.recipe} - {self.user}"


class Favorite(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        default_related_name = "favorites"
        unique_together = ("user", "recipe")

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class IngredientInRecipe(models.Model):
    """Модель ингредиентов в рецепте."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Количество"
    )

    class Meta:
        verbose_name = "Ингредиент для рецепта"
        verbose_name_plural = "Ингредиенты для рецепта"
        ordering = ("id",)
        unique_together = ("ingredient", "recipe")
