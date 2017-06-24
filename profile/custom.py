from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameModelBackend(object):
    """Login with username or email address"""
    def authenticate(self, username=None, password=None):
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(Q(username__iexact=username) | Q(email__iexact=username))

            if user.check_password(password):
                return user

        except User.DoesNotExist:
            return None

    def get_user(self, username):
        try:
            return get_user_model().objects.get(pk=username)
        except get_user_model().DoesNotExist:
            return None
