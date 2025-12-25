"""
Константы проекта Foodgram.
"""

MAX_LENGTH_EMAIL = 254
MAX_LENGTH_USERNAME = 150
MAX_LENGTH_FIRST_NAME = 150
MAX_LENGTH_LAST_NAME = 150
MAX_LENGTH_TAG_NAME = 32
MAX_LENGTH_TAG_SLUG = 32
MAX_LENGTH_INGREDIENT_NAME = 128
MAX_LENGTH_INGREDIENT_UNIT = 64
MAX_LENGTH_RECIPE_NAME = 256

MIN_COOKING_TIME = 1
MIN_INGREDIENT_AMOUNT = 1

ERROR_USERNAME_ME = "Имя пользователя 'me' недопустимо."
ERROR_USERNAME_INVALID = "Недопустимые символы в имени пользователя."
ERROR_TAGS_REQUIRED = "Нужен хотя бы один тег."
ERROR_TAGS_DUPLICATE = "Теги не должны повторяться."
ERROR_INGREDIENTS_REQUIRED = "Нужен хотя бы один ингредиент."
ERROR_INGREDIENTS_DUPLICATE = "Ингредиенты не должны повторяться."
ERROR_INGREDIENTS_NOT_EXIST = "Один или несколько ингредиентов не существуют"
ERROR_INGREDIENT_AMOUNT = "Кол-во ингредиента должно быть больше 0."
ERROR_SELF_SUBSCRIPTION = "Нельзя подписаться на самого себя."
ERROR_ALREADY_SUBSCRIBED = "Вы уже подписаны на этого пользователя."
ERROR_NOT_SUBSCRIBED = "Вы не подписаны на этого пользователя."
ERROR_RECIPE_ALREADY_ADDED = "Рецепт уже добавлен."
ERROR_RECIPE_NOT_ADDED = "Рецепт не был добавлен."
