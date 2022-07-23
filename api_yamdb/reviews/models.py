from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import year_validator

User = get_user_model()


class Genre(models.Model):
    """Available genres."""

    name = models.CharField(verbose_name='Название', max_length=256, )
    slug = models.SlugField(verbose_name='Идентификатор', max_length=50,
                            unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']


class Categories(models.Model):
    """Available categories."""

    name = models.CharField(verbose_name='Название', max_length=256, )
    slug = models.SlugField(verbose_name='Идентификатор', max_length=50,
                            unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']


class Title(models.Model):
    """Available titles, characterised in terms of year,
     genre, category and rating.
     """
    name = models.CharField(verbose_name='Название', max_length=200
                            )
    year = models.PositiveSmallIntegerField(verbose_name='Год выпуска',
                                            validators=[year_validator])
    genre = models.ManyToManyField(
        Genre, verbose_name='Жанр', through='TitlesGenres')
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL,
                                 related_name='titles', null=True)
    rating = models.PositiveSmallIntegerField(
        verbose_name='Оценка пользователей', null=True, default=None)
    description = models.TextField(verbose_name='Описание', blank=True,
                                   null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['name']


class TitlesGenres(models.Model):
    """Connecting model between genre and title."""

    title = models.ForeignKey(Title, verbose_name='Произведение',
                              on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, verbose_name='Жанр',
                              on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title} - жанр {self.genre}'

    class Meta:
        verbose_name = 'Произведение и Жанр'
        verbose_name_plural = 'Произведения и Жанры'


class Review(models.Model):
    """Model for reviews, connected with User model though author field."""
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(1, 'Допустимы значения от 1 до 10'),
            MaxValueValidator(10, 'Допустимы значения от 1 до 10')
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]


class Comment(models.Model):
    """Model for comment that users can make under reviews."""
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['pub_date']
