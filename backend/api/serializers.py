import base64
import re

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from foodgram.constants import (
    ERROR_INGREDIENT_AMOUNT,
    ERROR_INGREDIENTS_DUPLICATE,
    ERROR_INGREDIENTS_NOT_EXIST,
    ERROR_INGREDIENTS_REQUIRED,
    ERROR_TAGS_DUPLICATE,
    ERROR_TAGS_REQUIRED,
    ERROR_USERNAME_INVALID,
    ERROR_USERNAME_ME,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import CustomUser, Subscription


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для обработки изображений в base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Subscription.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(ERROR_USERNAME_ME)

        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(ERROR_USERNAME_INVALID)
        return value


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара."""

    avatar = Base64ImageField()

    class Meta:
        model = CustomUser
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте (чтение)."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте (запись)."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов для чтения."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Favorite.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )

    def validate(self, data):
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'tags': ERROR_TAGS_REQUIRED
            })

        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': ERROR_INGREDIENTS_REQUIRED
            })

        ingredient_list = []
        for item in ingredients:
            ingredient_id = item.get('id')
            if ingredient_id in ingredient_list:
                raise serializers.ValidationError({
                    'ingredients': ERROR_INGREDIENTS_DUPLICATE
                })
            ingredient_list.append(ingredient_id)

            amount = item.get('amount')
            if int(amount) < 1:
                raise serializers.ValidationError({
                    'ingredients': ERROR_INGREDIENT_AMOUNT
                })

        existing_count = Ingredient.objects.filter(
            id__in=ingredient_list).count()
        if len(ingredient_list) != existing_count:
            raise serializers.ValidationError({
                'ingredients': ERROR_INGREDIENTS_NOT_EXIST
            })

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({
                'tags': ERROR_TAGS_DUPLICATE
            })

        return data

    def create_ingredients(self, recipe, ingredients):
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        if tags is not None:
            instance.tags.set(tags)

        if ingredients is not None:
            instance.recipe_ingredients.all().delete()
            self.create_ingredients(instance, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context=self.context
        ).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Краткий сериализатор рецепта."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except (ValueError, TypeError):
                pass
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
