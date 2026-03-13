from django.contrib.auth.backends import ModelBackend


class VerifiedUserBackend(ModelBackend):

    def user_can_authenticate(self, user):
        if user.is_superuser:
            return True
        return super().user_can_authenticate(user) and user.is_verified
