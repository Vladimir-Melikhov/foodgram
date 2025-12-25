from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import (
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_USERNAME,
    MAX_LENGTH_FIRST_NAME,
    MAX_LENGTH_LAST_NAME,
)


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        'Электронная почта',
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGTH_FIRST_NAME,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGTH_LAST_NAME,
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='avatars/',
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
        verbose_name='Автор',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_subscription'
            ),
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
