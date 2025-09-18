from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import MinLengthValidator


class UserManager(BaseUserManager):
    def create_user(self, email, role, password=None):
        if email is None:
            raise TypeError("Users should have an Email")
        if role is None:
            raise TypeError("Users should have a role")

        user = self.model(email=self.normalize_email(email), role=role)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None):
        if password is None:
            raise TypeError("Password should not be none")

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


USER_ROLES = [("CONSUMER", "Consumer"), ("CREATOR", "Creator")]
CREATOR_TYPE_CHOICES = [
    ("MUSICIAN", "Musician"),
    ("PERFORMER", "Performer"),
    ("FILM_MAKER", "Film Maker"),
    ("COMEDIAN", "Comedian"),
    ("ORGANIZATION", "Organization"),
]


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    display_name = models.CharField(max_length=255, unique=True, null=True, blank=True)

    summary = models.TextField(null=True)
    role = models.CharField(
        max_length=255, choices=USER_ROLES, default=USER_ROLES[0][0]
    )
    job_description = models.TextField(null=True)
    job_name  = models.CharField(max_length=255, null=True, unique=True, db_index=True)
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    job_type = models.CharField(max_length=255, choices=CREATOR_TYPE_CHOICES, null=True)
    display_photo = models.ImageField(upload_to="display_photo/", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def signup_checklist(self):
        checklist = {
            "user_profile_completed": all(
                [
                    self.display_photo,
                    self.display_name,
                    self.summary,
                    self.city,
                    self.country
                ]
            ),
            "creator_profile_completed": all(
                [
                    self.role == CREATOR_TYPE_CHOICES[1][0],
                    self.job_description,
                    self.job_name,
                    self.job_type,
                ]
            ),
        }
        return checklist

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role"]

    objects = UserManager()

    def __str__(self):
        return f"{self.display_name} {self.email}"

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}

    class Meta:
        db_table = "users"


class EmailVerification(models.Model):
    is_verified = models.BooleanField(default=False)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    token = models.CharField(
        null=False, blank=False, max_length=6, validators=[MinLengthValidator(6)]
    )
    token_expiry = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "email_verifications"
