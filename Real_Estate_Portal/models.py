from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(User, auto_now=True)
    phone = models.PositiveIntegerField(default=0,blank=True)
    street = models.CharField(max_length=100,blank=True)
    city = models.CharField(max_length=100,blank=True)

    def __str__(self):
        return self.user.username
    
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile= Profile(user=instance)
        user_profile.save()

post_save.connect(create_profile, sender=User)


# Create your models here
# class CustomUser(AbstractUser):
#     email = models.EmailField(_("email address"), unique=True,max_length=254)
#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50)
#     phone = models.PositiveIntegerField(default=0)
#     street = models.CharField(max_length=100)
#     city = models.CharField(max_length=100,default='')
#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = []

#     objects = CustomUserManager()

#     def __str__(self):
#         return self.email

#class User(models.Model):
#    user = models.OneToOneField(User, on_delete=models.CASCADE)
#    user_ID= models.PositiveIntegerField(primary_key=True)
#    first_name = models.CharField(max_length=50)
#    last_name = models.CharField(max_length=50)
#    phone = models.PositiveIntegerField(default=0)
#    email = models.EmailField(max_length=50)
#    password = models.CharField(max_length=50)
#    street = models.CharField(max_length=100)
#    city = models.CharField(max_length=100,default='')
#
#    def __str__(self) -> str:
#       return f'{self.first_name} {self.last_name}'
    
class Property(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(default=0,decimal_places=2,max_digits=10)

    Category=[
    ('APARTMENT','Apartment'),
    ('VILLA','Villa'),
    ('HOUSE','House'),
    ('APARTMENT','Apartment'),
    ('OFFICE','Office'),
    ('STUDIO','Studio'),
    ('SHOP','Shop')
    ]
    category = models.CharField(choices=Category,max_length=10)
    description = models.CharField(max_length=500,default='',blank=True,null=True)
    image1 = models.ImageField(upload_to='images/properties/')
    image2 = models.ImageField(upload_to='images/properties/')
    image3 = models.ImageField(upload_to='images/properties/')
    size = models.PositiveIntegerField(default=1)
    Bathrooms=models.PositiveIntegerField(default=1)
    Bedrooms=models.PositiveIntegerField(default=1)
    seller_ID = models.PositiveIntegerField(default=0,null=True)
    Buy = models.BooleanField(default=False) #0=not sold 1=buy
    city= models.CharField(default='City',max_length=50)
    floor_number = models.PositiveIntegerField(default=1)
    apartment_number = models.PositiveIntegerField(default=1)
    installment_years = models.PositiveIntegerField(default=1)
    longitude= models.DecimalField(default=0,decimal_places=15,max_digits=19)
    latitude= models.DecimalField(default=0,decimal_places=15,max_digits=19)

    def __str__(self):
        return self.name

class Favorite(models.Model):
    user_ID = models.PositiveIntegerField(default=0)
    property_ID= models.PositiveIntegerField(default=0)