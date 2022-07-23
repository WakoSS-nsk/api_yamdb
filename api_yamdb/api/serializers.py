from rest_framework import serializers
from reviews.models import Categories, Genre, Title


class CategoriesSerializer(serializers.ModelSerializer):
    """Shows categories in two exact fields."""

    class Meta:
        model = Categories
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
        fields = ('name', 'slug')


class GenresSerializer(serializers.ModelSerializer):
    """Shows genres in two exact fields."""

    class Meta:
        model = Genre
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
        fields = ('name', 'slug')


class TitlesSerializer(serializers.ModelSerializer):
    """Allows creating titles."""

    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Categories.objects.all())

    class Meta:
        model = Title
        fields = '__all__'


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    """Shows objects while list command is used."""

    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True
    )
    genre = GenresSerializer(many=True, read_only=True)
    category = CategoriesSerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
