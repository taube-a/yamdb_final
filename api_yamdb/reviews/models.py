from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .validators import validate_username, validate_year

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

ROLE_CHOICES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):

    username = models.CharField(
        verbose_name='Юзернейм',
        validators=(validate_username,),
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
        max_length=254,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=255,
        choices=ROLE_CHOICES,
        default=USER
    )
    confirmation_code = models.CharField(
        'код подтверждения',
        max_length=255,
        null=True,
        blank=False,
        default='XXXX'
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True
    )

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_user(self):
        return self.role == USER

    class Meta:
        ordering = ('id',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self) -> str:
        return self.username


@receiver(post_save, sender=User)
def post_save(sender, instance, created, **kwargs):
    if created:
        confirmation_code = default_token_generator.make_token(
            instance
        )
        instance.confirmation_code = confirmation_code
        instance.save()


class Category(models.Model):

    name = models.CharField(
        verbose_name='Название категории',
        max_length=255
    )
    slug = models.SlugField(
        unique=True,
        max_length=settings.SLUG_FIELD_LENTH,
        verbose_name='URL-slug категории'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):

    name = models.CharField(
        verbose_name='Название жанра',
        max_length=255
    )
    slug = models.SlugField(
        unique=True,
        max_length=settings.SLUG_FIELD_LENTH,
        verbose_name='URL-slug жанра'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Title(models.Model):

    name = models.CharField(
        verbose_name='Название произведения',
        max_length=255
    )
    year = models.IntegerField(
        verbose_name='Год создания',
        validators=(validate_year,)
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        # through='GenreTitle',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Review(models.Model):

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.SmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
        verbose_name='Оценка',
        error_messages={'validators': 'Оценка должна быть от 1 до 10'}
    )
    pub_date = models.DateTimeField(
        verbose_name='Время добавления',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'

        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review'
            )
        ]
        ordering = ('pub_date',)


class Comment(models.Model):

    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        verbose_name='Время добавления',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('pub_date',)

    def __str__(self):
        return f'Отзыв {self.author.username} на {self.review.title.name}'
