import json
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def get_ingredients(self, file="ingredients.json"):
        BASE_DIR = Path(__file__).resolve().parent.parent
        file_path = f"{BASE_DIR}/data/{file}"
        try:
            with open(file_path, "r") as file:
                data = json.load(file)

                for item in data:
                    name = item["name"]
                    measurement_unit = item["measurement_unit"]

                    ingredient = Ingredient(
                        name=name, measurement_unit=measurement_unit
                    )
                    ingredient.save()

                self.stdout.write(
                    self.style.SUCCESS("Выполнено.")
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {str(e)}"))

    def handle(self, *args, **options):
        self.get_ingredients()
