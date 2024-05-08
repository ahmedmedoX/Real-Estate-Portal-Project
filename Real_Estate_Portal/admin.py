from django.contrib import admin
from .models import Favorite,Property, Profile
from django.contrib.auth.models import User
# Register your models here.

admin.site.register(Favorite)
admin.site.register(Property)
admin.site.register(Profile)

class ProfileInline(admin.StackedInline):
    model= Profile

class UserAdmin(admin.ModelAdmin):
    model=User
    field=["username","first_name","last_name","email"]
    inlines=[ProfileInline]
