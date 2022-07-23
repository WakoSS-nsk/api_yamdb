import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models

from .validations import validate_username


class User(AbstractUser):
    """
    The implementation of the definition of access rights for different users
    has been selected through the assignment of roles.
    """
    ALLOWED_ROLES = ('admin', 'moderator', 'user')
    DEFAULT_ROLE_INDEX = 2

    def token(self):
        """
        Allows you to get a user token by calling user.token, instead of
        user._generate_jwt_token(). The decorator @property above does this
        possible. the token is called a `dynamic property'.
        """
        return self._generate_jwt_token()

    # Рефакторинг требует здесь указать статик метод. Но тогда в role вернется
    # статик_объект, что приведет к ошибке, т.к. должна быть переменная
    def role_default():
        """Default user role for new customers."""
        return User.ALLOWED_ROLES[User.DEFAULT_ROLE_INDEX]

    def define_confirmation_code():
        """Get a five digit code by converting a random hex token."""
        token = secrets.token_hex(2)
        confirmation_code = int(token, 16)
        return confirmation_code
    # Username
    username = models.CharField(
        validators=(validate_username,),
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )

    # User-role field defining.
    role = models.SlugField(default=role_default)

    # Email field and email verifying.
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)

    confirmation_code = models.CharField(blank=True, null=True, max_length=128)

    bio = models.TextField(
        'Биография',
        blank=True,
    )

    def __str__(self):
        return f'{self.username}: AbstracUser instance.'
