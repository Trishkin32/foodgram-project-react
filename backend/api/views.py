from django.contrib.auth import get_user_model
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingList, Tag)
from users.models import Follow
from users.serializers import SubscriptionSerializer

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsOwnerOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer)
from .utils import extract_list

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Пользователь."""

    @action(
        methods=["GET"],
        permission_classes=(IsAuthenticated,),
        detail=False,
    )
    def me(self, request):
        self.get_object = self.get_instance
        return self.retrieve(request)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет тега."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет ингредиента."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецепта."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        return serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=(IsAuthenticated,),
        name="Добавить рецепт в избранное."
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object
        favorite, created = Favorite.objects.get_or_create(
            user=user, recipe=recipe
        )
        if not created:
            return Response(
                {"detail": "Рецепт уже добавлен в избранное."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def remove_favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object
        try:
            favorite = Favorite.objects.get(user=user, recipe=recipe)
        except Favorite.DoesNotExist:
            return Response(
                {'detail': 'Рецепт не найден в избранном.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object
        favorite, created = Favorite.objects.get_or_create(
            user=user, recipe=recipe
        )
        add_to_shopping_list, created = ShoppingList.objects.get_or_create(
            user=user, recipe=recipe
        )
        if created:
            serializer = FavoriteSerializer(add_to_shopping_list)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"detail": "Рецепт уже добавлен в корзину."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @shopping_cart.mapping.delete
    def remove_from_shopping_list(self, request, pk=None):
        user = request.user
        recipe = self.get_object

        try:
            favorite = ShoppingList.objects.get(user=user, recipe=recipe)
        except ShoppingList.DoesNotExist:
            return Response(
                {"detail": "Рецепт не найден в избранном."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientInRecipe.objects.filter(
                recipe__shopping_list__user=self.request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .order_by("ingredient__name")
            .annotate(amount=Sum("amount"))
        )
        return extract_list(self, request, ingredients)


class APISubscribe(APIView):
    """Вью-класс подписки пользователя."""

    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk=None):
        following = request.user

        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользователь не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if following == user:
            return Response(
                {"errors": "Вы не можете подписаться на себя."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow, created = Follow.objects.get_or_create(
            user=following,
            following=user,
        )
        if not created:
            return Response(
                {"errors": "Вы уже подписаны на этого автора."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = SubscriptionSerializer(user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        following = request.user

        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользователь не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            follow = Follow.objects.get(user=following, following=user)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response(
                {"errors": "Вы не подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SubscribeList(ListAPIView):
    """Вью-класс списка подписок пользователя."""

    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)
