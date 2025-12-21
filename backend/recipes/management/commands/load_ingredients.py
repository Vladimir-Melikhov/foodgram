import json
import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из JSON или CSV файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Путь к файлу с ингредиентами (JSON или CSV)'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        if file_path.endswith('.json'):
            self.load_from_json(file_path)
        elif file_path.endswith('.csv'):
            self.load_from_csv(file_path)
        else:
            self.stdout.write(
                self.style.ERROR('Поддерживаются только JSON и CSV файлы')
            )

    def load_from_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            ingredients = [
                Ingredient(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
                for item in data
            ]
            Ingredient.objects.bulk_create(
                ingredients,
                ignore_conflicts=True
            )
        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно загружено {len(ingredients)} ингредиентов из JSON'
            )
        )

    def load_from_csv(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            ingredients = [
                Ingredient(name=row[0], measurement_unit=row[1])
                for row in reader
            ]
            Ingredient.objects.bulk_create(
                ingredients,
                ignore_conflicts=True
            )
        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно загружено {len(ingredients)} ингредиентов из CSV'
            )
        )
