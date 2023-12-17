import base64
import io
from datetime import datetime as dt

from django.core.files.base import ContentFile
from django.http import HttpResponse
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Класс для преобразования картинки."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


def extract_list(self, request, ingredients):
    user = self.request.user
    filename = f"{user.username}_shopping_list.txt"

    today = dt.today()
    shopping_list = io.StringIO()
    shopping_list.write(
        f"Список покупок для пользователя: {user.username}\n\n"
    )
    shopping_list.write(f"Дата: {today:%Y-%m-%d}\n\n")
    shopping_list.write(
        "\n".join(
            [
                f'- {ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]})'
                f' - {ingredient["amount"]}'
                for ingredient in ingredients
            ]
        )
    )
    shopping_list.write(f"\n\nFoodgram ({today:%Y})")

    response = HttpResponse(
        shopping_list.getvalue().encode("utf-8"),
        content_type="text/plain; charset=utf-8",
    )
    response["Content-Disposition"] = f"attachment; filename={filename}"
    return response
