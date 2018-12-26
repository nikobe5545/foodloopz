from django.contrib.auth import get_user_model

# email == user name. Authentication made based on email only!
from django.contrib.auth.models import User


# Authenticating on email instead of username
class EmailBackend:
    @staticmethod
    def authenticate(request, username=None, password=None):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=username)
        except user_model.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
