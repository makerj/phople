from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.datetime_safe import date
from django.utils.translation import ugettext_lazy

import apiserver.util.aws as aws
from apiserver.util.misc import *


class S3Field(models.Field):
    description = ugettext_lazy("String (up to %(max_length)s)")

    def __init__(self, keyform, size_limit, *args, **kwargs):
        self.keyform = keyform
        self.size_limit = size_limit
        kwargs['max_length'] = 256
        super(S3Field, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(S3Field, self).deconstruct()
        kwargs['keyform'] = self.keyform
        kwargs['size_limit'] = self.size_limit
        kwargs['max_length'] = 256
        return name, path, args, kwargs

    def get_internal_type(self):
        return "CharField"

    def get_db_prep_save(self, value, connection):
        # Python -> Database
        if not value:
            return value
        if value.size >= self.size_limit:
            raise ValidationError('S3 file size limit exceeded. size is {}'.format(value.size))

        s3key = self.keyform.replace('{rand}', randstr(30)).format(value)
        aws.s3_put(s3key, value, value.size)
        return s3key

    def from_db_value(self, value, expression, connection, context):
        # Database -> Python
        # This function must be overridden. or value_to_string will not work properly
        return value

    def value_to_string(self, obj):
        # Database -> Serializer
        value = self.value_from_object(obj)
        return value if value in [None, ''] else aws.s3_get(value)


class Couple(models.Model):  # like group
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    coupling_begin = models.DateField(default=date.today)
    # users


class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        """
        Creates and saves a User with the given username and password
        """
        if not username:
            raise ValueError('Users must have username')

        user = self.model(
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        """
        Creates and saves a User with the given username and password
        """
        user = self.create_user(username=username,
                                password=password,
                                )
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    # mandatory ('password' is automatically created by django)
    username = models.CharField(max_length=129, unique=True, db_index=True)

    # properties
    name = models.CharField(max_length=35, blank=True)
    email = models.CharField(max_length=254, blank=True)  # maximum length of a valid email address (RFC 3696)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    age = models.IntegerField(blank=True, null=True)
    profile_image = S3Field('profile_image/{rand}_{}', mega(2), blank=True, null=True)
    profile_background_image = S3Field('profile_background_image/{rand}_{}', mega(5), blank=True, null=True)
    profile_message = models.CharField(max_length=35, blank=True)
    couple = models.ForeignKey(Couple, on_delete=models.SET_NULL, blank=True, null=True, db_index=True,
                               related_name='users')

    # metadata ('last_login' is automatically created by django)
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    social = JSONField(blank=True, null=True)

    # resolve django framework requirements
    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_superuser


class DatePost(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    couple = models.ForeignKey(Couple, on_delete=models.CASCADE, related_name='dataposts')
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=1000)
    tags = ArrayField(models.CharField(max_length=30), db_index=True)
    # datepostcomments
    # datepostmedias


class DatePostComment(models.Model):
    datepost = models.ForeignKey(DatePost, on_delete=models.CASCADE, related_name='datepostcomments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datepostcomments')
    message = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)


class DatePostMedia(models.Model):
    datepost = models.ForeignKey(DatePost, on_delete=models.CASCADE, related_name='datepostmedias')
    title = models.CharField(max_length=30)
    message = models.CharField(max_length=100)
    type = models.CharField(max_length=10)  # img, audio, video
    data = S3Field('datepostmedia/{rand}_{}', mega(200))
