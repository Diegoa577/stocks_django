# enconding: utf-8

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class UserRequestHistory(models.Model):
    """
    Model to store the requests done by each user.
    """
    date = models.DateTimeField()
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20)
    open = models.DecimalField(max_digits=10, decimal_places=2)
    high = models.DecimalField(max_digits=10, decimal_places=2)
    low = models.DecimalField(max_digits=10, decimal_places=2)
    close = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
        if self.pk is None:
            # If the Stock object is being created (not updated)
            try:
                stock_request = StockRequest.objects.get(symbol=self.symbol)
                stock_request.increment()
                stock_request.save()
            except StockRequest.DoesNotExist:
                StockRequest.objects.create(symbol=self.symbol, times_requested=1)

        super().save(*args, **kwargs)




class StockRequest(models.Model):
    symbol = models.CharField(max_length=20)
    times_requested = models.IntegerField(default=0)

    def increment(self):
        self.times_requested += 1
        self.save()
