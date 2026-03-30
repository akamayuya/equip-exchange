from django.contrib.auth.backends import ModelBackend


class VerifiedUserBackend(ModelBackend):

    def user_can_authenticate(self, user):
        if user.is_superuser:
            return True
        company = getattr(user, "company", None)
        is_verified = bool(company and company.is_verified)
        return super().user_can_authenticate(user) and is_verified
