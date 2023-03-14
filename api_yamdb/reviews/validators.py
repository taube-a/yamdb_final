import re

from django.core.exceptions import ValidationError
from django.utils import timezone

ME = ['me', 'ME', 'Me', 'mE']


def validate_username(username):
    if username in ME:
        raise ValidationError(
            ('Юзернейм пользователя не может быть "%(username)s".'),
            params={'username': username},
        )
    if re.search(r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$', username) is None:
        raise ValidationError(
            (f'Не допустимые символы <{username}> в нике.'),
            params={'username': username},
        )


def validate_year(value):
    now = timezone.now().year
    if value > now:
        raise ValidationError(
            f'Год должен не больше текущего: {now}'
        )
