from django.core.exceptions import ValidationError

from users.constants import (
    MAX_AMOUNT,
    MAX_COOKING,
    MIN_AMOUNT,
    MIN_COOKING,
)


def real_time(value):
    """
    Проверяет, находится ли время приготовления в заданном диапазоне.

    Параметры:
    value (int): Время в минутах.

    Исключение:
    В случае, если значение не находится в допустимом диапазоне,
    возникает ValidationError с сообщением об ошибке.
    """
    if not MIN_COOKING <= value < MAX_COOKING:
        raise ValidationError(
            'Укажите время в диапазоне от 1 минуты до 32 000 минут.'
        )


def real_amount(value):
    """
    Проверяет, находится ли количество ингредиентов в заданном диапазоне.

    Параметры:
    value (int): Количество ингредиентов.

    Исключение:
    В случае, если значение не находится в допустимом диапазоне,
    возникает ValidationError с сообщением об ошибке.
    """
    if not MIN_AMOUNT <= value < MAX_AMOUNT:
        raise ValidationError(
            'Укажите количество в диапазоне от 1 до 32 000.'
        )
