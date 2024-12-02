from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from users.constants import (USERNAME_REGEX, MAX_LENGTH_USERNAME,
                             MAX_LENGTH_F_NAME, MAX_LENGTH_L_NAME
                             )


class User(AbstractUser):
    """Модель представления пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',
                       'first_name',
                       'last_name'
                       )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGTH_F_NAME
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGTH_L_NAME
    )
    username = models.CharField(
        'Имя пользователя',
        unique=True,
        max_length=MAX_LENGTH_USERNAME,
        validators=[RegexValidator(
            regex=USERNAME_REGEX,
            message='Недопустимый символ'
        )]
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        blank=True,
        null=True,
        default=None,
        upload_to='profiles/avatars/'
    )
    email = models.EmailField(
        'Адрес эл.почты',
        unique=True,
        max_length=254
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribtion(models.Model):
    """Подписка пользователя на пользователя"""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='following',
                             verbose_name='Пользователь'
                             )

    following = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='followers',
                                  verbose_name='Подписчик'
                                  )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'following'],
                                    name='unique_following'),
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.following.username}'
