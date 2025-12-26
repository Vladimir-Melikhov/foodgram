from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    CustomUserSerializer,
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeSerializer,
    RecipeShortSerializer,
    SubscriptionSerializer,
    TagSerializer,
)
from foodgram.constants import (
    ERROR_ALREADY_SUBSCRIBED,
    ERROR_NOT_SUBSCRIBED,
    ERROR_RECIPE_ALREADY_ADDED,
    ERROR_RECIPE_NOT_ADDED,
    ERROR_SELF_SUBSCRIPTION,
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


class CustomUserViewSet(DjoserUserViewSet):
    """Вьюсет для пользователей."""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPageNumberPagination

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        user.avatar.delete()
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        subscriptions = CustomUser.objects.filter(
            subscribed_to__user=request.user
        )
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(CustomUser, id=id)

        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'errors': ERROR_SELF_SUBSCRIPTION},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subscription, created = Subscription.objects.get_or_create(
                user=request.user,
                author=author
            )

            if not created:
                return Response(
                    {'errors': ERROR_ALREADY_SUBSCRIBED},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = SubscriptionSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = Subscription.objects.filter(
            user=request.user,
            author=author
        )

        if not subscription.exists():
            return Response(
                {'errors': ERROR_NOT_SUBSCRIBED},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        permission_classes=[AllowAny]
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = f"{request.build_absolute_uri('/recipes/')}{recipe.id}/"
        return Response({'short-link': short_link})

    def add_to(self, model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        obj, created = model.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )

        if not created:
            return Response(
                {'errors': ERROR_RECIPE_ALREADY_ADDED},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        obj = model.objects.filter(user=request.user, recipe=recipe)

        if not obj.exists():
            return Response(
                {'errors': ERROR_RECIPE_NOT_ADDED},
                status=status.HTTP_400_BAD_REQUEST
            )

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        return self.add_to(Favorite, request, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.delete_from(Favorite, request, pk)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        return self.add_to(ShoppingCart, request, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.delete_from(ShoppingCart, request, pk)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_carts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.pdf"'
        )

        p = canvas.Canvas(response, pagesize=A4)

        p.setFont('Helvetica', 14)
        p.drawString(100, 800, 'Shopping List')

        y = 750
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['total_amount']
            text = f"{name} ({unit}) - {amount}"
            p.drawString(100, y, text)
            y -= 20
            if y < 50:
                p.showPage()
                p.setFont('Helvetica', 14)
                y = 800

        p.showPage()
        p.save()

        return response
