# backends.py - Custom Authentication Backend

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in with email
    instead of username.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate using email address
        """
        if username is None:
            username = kwargs.get('email')
        
        if username is None or password is None:
            return None
        
        try:
            # Try to fetch the user by searching the email field
            user = User.objects.get(
                Q(email=username) | Q(username=username),
                is_active=True,
                is_deleted=False
            )
            
            # Check the password
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Multiple users with the same email (shouldn't happen with unique constraint)
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        Get a user by their primary key
        """
        try:
            return User.objects.get(pk=user_id, is_active=True, is_deleted=False)
        except User.DoesNotExist:
            return None