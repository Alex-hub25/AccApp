from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    """Custom user model — email is the primary identifier."""
    email = models.EmailField(unique=True)

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return self.email


class Company(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),
        ('JPY', 'Japanese Yen'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')
    name = models.CharField(max_length=200)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    fiscal_year_start = models.PositiveSmallIntegerField(
        default=1, help_text='Month number (1=January) when the fiscal year starts'
    )
    address = models.TextField(blank=True)
    tax_number = models.CharField(max_length=50, blank=True, verbose_name='Tax/VAT Number')
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'companies'
        ordering = ['name']

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    active_company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='+'
    )

    def __str__(self):
        return f'Profile({self.user.email})'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
