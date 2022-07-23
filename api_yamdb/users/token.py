from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """
    Token generation if the correct username and confirmation_code are
    received.
    """
    refresh = RefreshToken.for_user(user)
    # Required scopes: according to ReDoc
    refresh['write'] = user.role

    return {
        'Token': str(refresh.access_token)
    }
