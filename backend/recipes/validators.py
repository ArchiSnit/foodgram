from django.core.exceptions import ValidationError

from users.constants import (
    MIN_AMOUNT,
    MAX_AMOUNT,
    MIN_COOKING,
    MAX_COOKING,
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
            'Укажите количество в диапазоне от 1 до 42000.'
        )


def actual_cooking_time(value):
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
            'Укажите время в диапазоне от 1 минуты до 10080 минут.'
        )
