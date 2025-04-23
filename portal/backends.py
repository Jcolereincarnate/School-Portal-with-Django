from django.contrib.auth.backends import BaseBackend
from .models import StudentProfile

class MatricNumberAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            student = StudentProfile.objects.get(matric_number=username)
            user = student.user
            if user.check_password(password):
                return user
        except StudentProfile.DoesNotExist:
            return None

    def get_user(self, user_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None