from django.contrib.auth.models import AbstractUser
from django.db import models


class UserUser(AbstractUser):
    """Переопределенная модель пользователя."""

    class Roles(models.TextChoices):
        USER = "user"
        MODERATOR = "moderator"
        ADMIN = "admin"

    role = models.CharField(
        "Роль",
        max_length=256,
        default=Roles.USER,
        choices=Roles.choices,
    )
    email = models.EmailField(
        "Электронная почта",
        max_length=254,
        unique=True,
        error_messages={
            "unique": "Пользователь с такой электронной почтой уже существует."
        },
    )
    first_name = models.CharField(
        "Имя",
        max_length=150,
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=150,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
    ]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == "admin" or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == "moderator"


class Follow(models.Model):
    """Модель подписчика."""

    user = models.ForeignKey(
        UserUser,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Пользователь"
    )
    following = models.ForeignKey(
        UserUser,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Подписчик"
    )

    class Meta:
        unique_together = ["user", "following"]
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики"

    def __str__(self):
        return f"{self.user} подписан на {self.following}"
