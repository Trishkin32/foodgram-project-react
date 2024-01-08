import re

from django.core.exceptions import ValidationError

ERROR_NAME = ('me',)


def validate_username(username):
    if not re.match(r'^[\w.@+-]+\Z', username):
        raise ValidationError(
            'Неверный формат имени пользователя'
        )
    if username in ERROR_NAME:
        raise ValidationError(
            f'Имя пользователя "{username}" запрещено!'
        )
    return username
