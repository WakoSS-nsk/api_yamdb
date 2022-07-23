from django.core.mail import EmailMessage
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site

from rest_framework import permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from .serializers import (
    TokenSerializer,
    UserSerializer,
    UserAllFieldSerializer
)
from .permissions import RoleBasedPermission
from .models import User
from .token import get_tokens_for_user


class SignUpViewSet(APIView):
    """
    Self-registration of a user with a POST request to endpoint
    `/api/v1/auth/signup/`.
    """
    permission_classes = (permissions.AllowAny,)

    def send_email_action(self, user, request):
        """
        Sending an email after receiving a POST request for registration.
        The self argument contains the user object.
        """
        current_site = get_current_site(request)
        email_subject = 'Activate your account.'

        confirmation_code = User.define_confirmation_code()
        hashed_confirmation_code = make_password(confirmation_code)

        user.confirmation_code = hashed_confirmation_code
        user.save()

        email_body = (
            f'Hi, {user.username}. Send to `{current_site}` your username and '
            'this confirmation_code to `/api/v1/auth/token/`:\n'
            f'{confirmation_code}'
        )

        email = EmailMessage(subject=email_subject, body=email_body,
                             to=[user.email])
        email.send()

    def post(self, request):
        """
        A pre check is enabled to see if this user has already beencreated
        before.
        """
        if User.objects.filter(username=request.data.get('username')).exists():
            user = User.objects.get(
                username=request.data.get('username')
            )
            if user.confirmation_code is None:
                self.send_email_action(user, request)
                return Response(
                    request.data,
                    status=status.HTTP_200_OK
                )

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = User.objects.get(username=request.data.get('username'))

        self.send_email_action(user, request)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CustomTokenView(APIView):
    """
    Checking the POST request to the address `/api/v1/auth/token/`.
    Providing a uuid4 token if the correct data is sent.
    """

    def post(self, request, format=None):
        """Processing POST request only."""

        serializer = TokenSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = User.objects.get(username=request.data['username'])
        user.is_email_verified = True
        user.save()

        response_data = get_tokens_for_user(user)

        return Response(
            response_data,
            status=status.HTTP_200_OK
        )


class UsersView(viewsets.ModelViewSet):
    """
    RoleBasedPermission is used.
    Requires an additional `allowed_roles` argument
    in the form of a list or tuple containing allowed user roles.
    """
    queryset = User.objects.all()
    serializer_class = UserAllFieldSerializer
    permission_classes = [RoleBasedPermission]
    allowed_roles = ('admin',)
    lookup_field = 'username'

    @action(
        methods=["get", "patch"],
        detail=False,
        url_path="me",
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserAllFieldSerializer,
    )
    def users_me(self, request):
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        if request.method == "PATCH":
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
