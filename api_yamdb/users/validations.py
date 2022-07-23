from django.core.exceptions import ValidationError
from rest_framework.exceptions import APIException
from rest_framework import status


def validate_username(value):
    if len(value) < 3:
        raise ValidationError(
            ('Имя пользователя не может быть менее 3 символов.'),
            params={'value': value},
        )


class Custom404Validation(APIException):
    status_code = status.HTTP_404_NOT_FOUND
