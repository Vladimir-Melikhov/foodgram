
echo "Запуск настройки проекта Foodgram..."

echo "Применение миграций..."
python manage.py migrate

echo "Загрузка ингредиентов..."
if [ -f "../data/ingredients.json" ]; then
    python manage.py load_ingredients ../data/ingredients.json
elif [ -f "../data/ingredients.csv" ]; then
    python manage.py load_ingredients ../data/ingredients.csv
else
    echo "Файлы с ингредиентами не найдены!"
fi

# Сбор статики
echo "Сбор статических файлов..."
python manage.py collectstatic --no-input

# Создание суперпользователя (интерактивно)
echo "Создание суперпользователя..."
python manage.py createsuperuser

echo "Настройка завершена!"
echo "Запустите сервер командой: python manage.py runserver"