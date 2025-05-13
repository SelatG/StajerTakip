from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomPermission(models.Model):
    code_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code_name

    class Meta:
        verbose_name = "Özel Yetki"
        verbose_name_plural = "Özel Yetkiler"


class CustomRole(models.Model):
    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField(CustomPermission, blank=True)

    def __str__(self):
        return self.name

    def has_permission(self, permission_codename):
        return self.permissions.filter(code_name=permission_codename, is_active=True).exists()

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roller"


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError("Email zorunludur")
        if not role:
            raise ValueError("Rol zorunludur")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        admin_role, _ = CustomRole.objects.get_or_create(name='Admin')  # Admin rolü oluşturuluyor
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, role=admin_role, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role = models.ForeignKey(CustomRole, on_delete=models.CASCADE, related_name="users")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    status = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    def __str__(self):
        return self.email

    def has_permission(self, permission_codename):
        return self.role.has_permission(permission_codename)

    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"


# Student modeli
class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    student_number = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    faculty = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Company modeli
class Company(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='company_profile')
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    contact_person = models.CharField(max_length=100)
    website = models.URLField(blank=True, null=True)
    tax_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
