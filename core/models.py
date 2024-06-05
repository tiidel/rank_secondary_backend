from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.utils.translation import gettext_lazy as _
import jwt
import uuid
from django_extensions.db.models import TimeStampedModel, ActivatorModel

from safedelete.models import SafeDeleteModel
from django.contrib.postgres.fields import ArrayField

# Create your models here.
from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.models import Group
from django.db import migrations
from django.utils.text import slugify


from datetime import datetime, timedelta
from helper.models import TrackingModel
from helper.enum import UserRole


class customUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError("The given username must be set")
        if not email:
            raise ValueError("The given email must be set")
        
        email = self.normalize_email(email)
        
        # GlobalUserModel = apps.get_model(
        #     self.model._meta.app_label, self.model._meta.object_name
        # )
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user



    def create_user(self, email, username=None, password=None, **extra_fields):
        
        if not username:

            if "first_name" in extra_fields and "last_name" in extra_fields:
                username = self.generate_username(extra_fields["first_name"], extra_fields["last_name"])

            else:
                raise ValueError("Username cannot be generated without first name and last name")

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(username, email, password, **extra_fields)



    def create_superuser(self, email, username=None,  password=None, **extra_fields):
        
        if not username:
            if "first_name" in extra_fields and "last_name" in extra_fields:
                username = self.generate_username(extra_fields["first_name"], extra_fields["last_name"])

            else:
                raise ValueError("Username cannot be generated without first name and last name")
            
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)




    def generate_username(self, first_name, last_name):
        """
        Generate a username based on the first name and last name.
        """
       
        base_username = self.model.normalize_username(first_name + last_name)
        username = base_username
        counter = 1
       
        while self.model.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        return username


class User(AbstractBaseUser, PermissionsMixin, TrackingModel):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """
    pass
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        blank=True,
        help_text=_(
            "Optional. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    
    email = models.EmailField(_("email address"), blank=False, unique=True)
    
    date_of_birth = models.DateField(null=True, blank=True)
    
    avatar = models.ImageField(upload_to='images', null=True, blank=True)
    
    phone = models.CharField(_("Mobile contact number"), max_length=20, null=True, blank=False)
    
    phone_alt = models.CharField(_("Alternate contact information"), max_length=20, null=True, blank=True)
    
    address = models.CharField(_('location of residence of user'), max_length=256, null=True, blank=True)

    role = models.CharField(_("User role"), max_length=50, null=True, blank=True, choices=UserRole.choices)
    
    bio = models.CharField(_("Some content about user"), max_length=50, null=True, blank=True)
    
    address_alt = models.CharField(_('location of residence of user'), max_length=256, null=True, blank=True)

    school_code = models.CharField(_("Code from school where user belongs"), max_length=15, null=False, blank=True)
    
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    
    email_verified = models.BooleanField(
        _("email_verified"),
        default=False,
        help_text=_(
            "Designates whether this user email is verified "
        ),
    )

    schools = ArrayField(models.CharField(_("list of school tenants"), max_length=100), default=list)
    
    school = models.CharField(_("name of school"), max_length=250, default='university')

    gender = models.CharField(max_length=50, null=True, blank=True)
    

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = customUserManager()

    def save(self, *args, **kwargs):
       
        if not self.username:

            base_username = slugify(self.first_name + self.last_name)
            username = base_username
            counter = 1

            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
        
            self.username = username
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class SchoolBaseModel(TimeStampedModel, ActivatorModel, SafeDeleteModel):
    
    id = models.UUIDField(
        default=uuid.uuid4, null=False, blank=False, unique=True, primary_key=True
    )
    
    is_deleted = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(_("registration date"), auto_now_add=True)
    
    update_at = models.DateTimeField(_("modification of model"), auto_now=True)
    
    created_by = models.CharField( _("Email of user who creates model"), max_length=100, null=True, blank=True)

    updated_by = models.CharField( _("Email of user who creates model"), max_length=100, null=True, blank=True)
    
    
class BaseModel(TimeStampedModel, ActivatorModel, SafeDeleteModel):
    
    id = models.UUIDField(
        default=uuid.uuid4, null=False, blank=False, unique=True, primary_key=True
    )
    
    is_deleted = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(_("registration date"), auto_now_add=True)
    
    update_at = models.DateTimeField(_("modification of model"), auto_now=True)
    
    created_by = models.CharField( _("Email of user who creates model"), max_length=100, null=True, blank=True)

    updated_by = models.CharField( _("Email of user who creates model"), max_length=100, null=True, blank=True)
    
    # school = models.ForeignKey("school.School", related_name="school", on_delete = models.CASCADE)
    

