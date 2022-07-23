from django.core.exceptions import ValidationError
from django.utils import timezone


def year_validator(value):
    """Validates that entered year is not greater then current."""
    if value > timezone.now().year:
        raise ValidationError(
            ('Год %(value)s больше текущего!'),
            params={'value': value},
        )
