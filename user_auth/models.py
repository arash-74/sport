from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.save(using=self._db)
        return user
    def create_superuser(self,email, password,**extra_fields):
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email,password,**extra_fields)


class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True,verbose_name='ایمیل')
    first_name = models.CharField(max_length=100,blank=True,verbose_name='نام')
    last_name = models.CharField(max_length=100,blank=True,verbose_name='نام خانوادگی')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    bio = models.TextField(null=True,blank=True)
    address = models.TextField(verbose_name='آدرس',null=True)
    phone = models.CharField(verbose_name='تلفن',null=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        verbose_name='کاربر'
        verbose_name_plural = 'کاربرها'
    def save(self,*args,**kwargs):
        if not self.password:
            self.set_unusable_password()
        super().save(*args,**kwargs)

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'