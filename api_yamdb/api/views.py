from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.exceptions import ParseError

from reviews.models import (Categories, Genre, Review,
                            Title)
from reviews.serializers import (ReviewSerializer, CommentSerializer)

from .filters import TitlesFilter
from .mixins import CreateListDestroyViewSet
from .permissions import (
    IsAdminOrReadOnly,
    IsAdminModerAuthorOrReadOnly
)
from .serializers import (
    CategoriesSerializer,
    GenresSerializer,
    ReadOnlyTitleSerializer,
    TitlesSerializer
)


class CategoriesViewSet(CreateListDestroyViewSet):
    """Shows name and slug of a category."""

    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenresViewSet(CreateListDestroyViewSet):
    """Shows name and slug of a genre."""

    queryset = Genre.objects.all()
    serializer_class = GenresSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitlesViewSet(viewsets.ModelViewSet):
    """Shows titles' name, score, category and genre."""

    queryset = Title.objects.all().annotate(
        Avg("reviews__score")
    ).order_by("name")
    serializer_class = TitlesSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        """Chooses serializer dependently on action."""
        if self.action in ("retrieve", "list"):
            return ReadOnlyTitleSerializer
        return TitlesSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModerAuthorOrReadOnly,)

    def get_queryset(self):
        return Review.objects.filter(title=self.kwargs.get("title_id"))

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs["title_id"])
        try:
            serializer.save(author=self.request.user, title=title)
        except IntegrityError:
            raise ParseError(detail="Автор уже оставил отзыв")


class CommentViewSet(viewsets.ModelViewSet):
    """Shows comments under review with it's author."""
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModerAuthorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)
