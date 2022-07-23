from django.contrib.auth.hashers import check_password
from django.contrib.auth.validators import UnicodeUsernameValidator

from rest_framework import serializers

from .validations import Custom404Validation
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Validation of user fields during registration."""

    def create(self, validated_data):
        """
        Check the required fields for signup data.The assignment of the
        validation code is done at the serialization stage, since it will be
        necessary to additionally use the save() method in the View Set.
        """
        User.objects.create(**validated_data)
        return validated_data

    class Meta:
        model = User
        fields = ['username', 'email']


class UserAllFieldSerializer(serializers.ModelSerializer):
    """Primitive checking only by model fields."""
    def validate_role(self, value):
        """Checking the role for an existing value."""
        request = self.context['request']
        user = request.user

        if value not in User.ALLOWED_ROLES:
            raise serializers.ValidationError(
                'Check that you have specified the correct value of the `role`'
                ' field.'
            )

        if user.role != User.ALLOWED_ROLES[0]:
            return user.role

        return value

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        ]


class TokenSerializer(serializers.Serializer):
    """
    The base class of the serializer is used. Otherwise, the validation of the
    username field assumes that the name must be unique.
    """
    username = serializers.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()]
    )
    confirmation_code = serializers.CharField(max_length=128)

    def validate(self, data):
        """
        Checking that a user with the same name exists.
        Checking that the confirmation_code matches the one sent by mail.
        """

        if not User.objects.filter(username=data['username']).exists():
            invalid_username = (
                'Please make sure that the username you sent '
                'is correct.'
            )
            raise Custom404Validation(
                {'username': invalid_username}
            )

        user = User.objects.get(username=data['username'])

        if not check_password(
            data['confirmation_code'],
            user.confirmation_code
        ):
            invalid_code = (
                'Please make sure that you have entered the correct '
                'confirmation code.'
            )
            raise serializers.ValidationError(
                {'confirmation_code': invalid_code}
            )

        return data

    class Meta:
        model = User
        fields = ['username', 'confirmation_code']
