from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
import pathlib
import uuid
from django.utils.text import slugify
from django.db import models
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


def set_filename(new_filename, filename: str) -> str:
    return (f"{slugify(new_filename)}-{uuid.uuid4()}"
            + pathlib.Path(filename).suffix)


def profile_picture_path(instance, filename: str) -> pathlib.Path:
    return pathlib.Path(
        "upload/" + instance.__class__.__name__.lower()
    ) / pathlib.Path(
        set_filename(instance.full_name + "-" + instance.email, filename)
    )


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    bio = models.TextField(_("bio"), blank=True)
    profile_picture = models.ImageField(
        null=True,
        blank=True,
        upload_to=profile_picture_path
    )
    followers = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followed_by",
        blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return self.email
